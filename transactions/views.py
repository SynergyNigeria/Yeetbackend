from decimal import Decimal
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction as db_transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from accounts.models import User
from notifications.models import Notification
from .models import Transaction, TransactionReport
from .serializers import TransactionSerializer, TransactionCreateSerializer, TransactionReportSerializer, CreateTransactionReportSerializer
from .services import TransferService


class TransactionViewSet(viewsets.ModelViewSet):
    """Main transaction viewset with YEET transfer functionality"""
    
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter transactions where user is sender or recipient
        user = self.request.user
        return Transaction.objects.filter(
            Q(sender=user) | Q(recipient=user)
        ).order_by('-created_at')
        
    @action(detail=False, methods=['post'])
    def yeet_transfer(self, request):
        """Create a new YEET transfer with full banking rules validation"""
        data = request.data
        user = request.user
        
        try:
            # Extract data
            recipient_account = data.get('recipient_account', '').strip()
            amount = data.get('amount')
            transfer_pin = data.get('transfer_pin', '')
            message = data.get('message', '').strip()
            
            # Validate amount
            if not amount:
                return Response(
                    {'error': 'Amount is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                amount = Decimal(str(amount))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid amount format'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if this is an internal or external transfer
            is_internal = False
            try:
                recipient = User.objects.get(account_number=recipient_account)
                is_internal = True
            except User.DoesNotExist:
                is_internal = False
            
            # Process the transfer using the service
            if is_internal:
                success, transaction_obj, message_result = TransferService.process_internal_transfer(
                    user, recipient_account, amount, transfer_pin, message
                )
            else:
                success, transaction_obj, message_result = TransferService.process_external_transfer(
                    user, recipient_account, amount, transfer_pin, message
                )
            
            if success:
                serializer = self.get_serializer(transaction_obj)
                return Response({
                    'success': True,
                    'message': message_result,
                    'transaction': serializer.data,
                    'new_balance': user.balance
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'error': message_result}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except Exception as e:
            return Response(
                {'error': f'Transfer failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def wire_transfer(self, request):
        """Create a new wire transfer with banking rules validation"""
        data = request.data
        user = request.user
        
        try:
            # Extract data
            recipient_info = data.get('recipient_info', {})
            amount = data.get('amount')
            transfer_pin = data.get('transfer_pin', '')
            message = data.get('message', '').strip()
            
            # Validate amount
            if not amount:
                return Response(
                    {'error': 'Amount is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                amount = Decimal(str(amount))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'Invalid amount format'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if amount <= 0:
                return Response(
                    {'error': 'Amount must be positive'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not recipient_info:
                return Response(
                    {'error': 'Recipient information is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check transfer eligibility
            can_transfer, eligibility_message = user.can_transfer()
            if not can_transfer:
                return Response(
                    {'error': eligibility_message}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate transfer PIN (unless prime account)
            if not user.is_prime:
                if not transfer_pin:
                    return Response(
                        {'error': 'Transfer PIN is required'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                if not user.check_transfer_pin(transfer_pin):
                    return Response(
                        {'error': 'Invalid transfer PIN'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Calculate total with wire fee
            wire_fee = Decimal('15.00')  # Wire transfer fee
            total_amount = amount + wire_fee
            
            if user.balance < total_amount:
                return Response(
                    {'error': f'Insufficient balance. Required: ${total_amount} (including ${wire_fee} fee)'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Process the wire transfer
            with db_transaction.atomic():
                user.balance -= total_amount
                user.save()
                
                # Create transaction record
                transaction_obj = Transaction.objects.create(
                    transaction_type='WIRE',
                    amount=amount,
                    description=message or f'Wire transfer to {recipient_info.get("name", "External")}',
                    sender=user,
                    recipient=None,  # No internal recipient for wire transfers
                    recipient_account=recipient_info.get('account', ''),
                    status='COMPLETED',
                    completed_at=timezone.now()
                )
                
                # Create notification
                Notification.objects.create(
                    user=user,
                    title='💳 Wire Transfer Sent',
                    message=f'Wire transfer of ${amount} sent successfully. Fee: ${wire_fee}',
                    notification_type='TRANSACTION',
                    transaction=transaction_obj
                )
            
            serializer = self.get_serializer(transaction_obj)
            return Response({
                'success': True,
                'message': f'Wire transfer completed successfully. Fee: ${wire_fee}',
                'transaction': serializer.data,
                'new_balance': user.balance
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'Wire transfer failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        """Get current user's transactions"""
        transactions = self.get_queryset()
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def account_summary(self, request):
        """Get account summary with balance and transaction stats"""
        user = request.user
        transactions = self.get_queryset()
        
        # Calculate stats
        total_sent = sum(t.amount for t in transactions if t.sender == user)
        total_received = sum(t.amount for t in transactions if t.recipient == user)
        transaction_count = transactions.count()
        
        return Response({
            'balance': user.balance,
            'account_number': user.account_number,
            'account_level': user.get_account_level(),
            'is_verified': user.is_verified,
            'has_deposit': user.has_deposit,
            'is_prime': user.is_prime,
            'can_transfer': user.can_transfer()[0],
            'transfer_eligibility_message': user.can_transfer()[1],
            'total_sent': total_sent,
            'total_received': total_received,
            'transaction_count': transaction_count,
            'recent_transactions': TransactionSerializer(
                transactions[:5], many=True
            ).data
        })


# Keep existing class-based views for compatibility
class TransactionListView(generics.ListAPIView):
    """List user transactions"""
    
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination for transactions
    
    def get_queryset(self):
        return Transaction.objects.filter(
            Q(sender=self.request.user) | Q(recipient=self.request.user)
        ).order_by('-created_at')


class TransactionCreateView(generics.CreateAPIView):
    """Create a new transaction"""
    
    serializer_class = TransactionCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with db_transaction.atomic():
            transaction_obj = serializer.save()
            
            # Update balances
            user = request.user
            amount = transaction_obj.amount
            
            if transaction_obj.transaction_type == 'DEPOSIT':
                user.balance += amount
                transaction_obj.status = 'COMPLETED'
                transaction_obj.completed_at = transaction_obj.created_at
            
            elif transaction_obj.transaction_type in ['WITHDRAWAL', 'TRANSFER', 'PAYMENT']:
                user.balance -= amount
                transaction_obj.status = 'COMPLETED'
                transaction_obj.completed_at = transaction_obj.created_at
                
                # If it's a transfer, credit the recipient
                if transaction_obj.transaction_type == 'TRANSFER' and transaction_obj.recipient:
                    transaction_obj.recipient.balance += amount
                    transaction_obj.recipient.save()
            
            user.save()
            transaction_obj.save()
        
        return Response(TransactionSerializer(transaction_obj).data, status=status.HTTP_201_CREATED)


# Function-based views for specific endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recent_transactions_view(request):
    """Get recent transactions for dashboard"""
    
    transactions = Transaction.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).order_by('-created_at')[:5]
    
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_receiver_view(request):
    """Validate receiver by account number"""
    
    account_number = request.data.get('account_number')
    
    if not account_number:
        return Response(
            {'error': 'Account number is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(account_number=account_number)
        
        # Don't allow self-transfer
        if user == request.user:
            return Response(
                {'error': 'Cannot transfer to your own account'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'valid': True,
            'receiver': {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'account_number': user.account_number
            }
        })
        
    except User.DoesNotExist:
        return Response(
            {'valid': False, 'error': 'Account number not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


class TransactionReportViewSet(viewsets.ModelViewSet):
    """ViewSet for transaction reports"""
    
    queryset = TransactionReport.objects.all()
    serializer_class = TransactionReportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return TransactionReport.objects.filter(reporter=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateTransactionReportSerializer
        return TransactionReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)
        
        # Create notification for user
        Notification.objects.create(
            user=self.request.user,
            title='📋 Transaction Report Submitted',
            message=f'Your report for transaction {serializer.instance.transaction.transaction_id} has been submitted and is under review.',
            notification_type='SYSTEM'
        )
        
        # TODO: Create notification for admin/support staff
        # This would require identifying admin users and notifying them


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_transaction_report(request):
    """Create a transaction report"""
    
    serializer = CreateTransactionReportSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        report = serializer.save(reporter=request.user)
        
        # Create notification for user
        Notification.objects.create(
            user=request.user,
            title='📋 Transaction Report Submitted',
            message=f'Your report for transaction {report.transaction.transaction_id} has been submitted and is under review.',
            notification_type='SYSTEM'
        )
        
        response_serializer = TransactionReportSerializer(report)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transaction_reports(request):
    """Get user's transaction reports"""
    
    reports = TransactionReport.objects.filter(reporter=request.user)
    serializer = TransactionReportSerializer(reports, many=True)
    return Response(serializer.data)
