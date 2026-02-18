from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ChatRoom, ChatMessage, ChatRoomMembership

User = get_user_model()


class ChatModelTests(TestCase):
    """Test chat models"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com', 
            password='testpass123'
        )
        self.support_user = User.objects.create_user(
            username='support',
            email='support@example.com',
            password='testpass123',
            is_staff=True
        )
    
    def test_create_chat_room(self):
        """Test creating a chat room"""
        room = ChatRoom.objects.create(
            name='Test Room',
            room_type='USER_SUPPORT'
        )
        room.participants.add(self.user1, self.support_user)
        
        self.assertEqual(room.participants.count(), 2)
        self.assertTrue(room.participants.filter(id=self.user1.id).exists())
        self.assertTrue(room.participants.filter(id=self.support_user.id).exists())
    
    def test_create_message(self):
        """Test creating a chat message"""
        room = ChatRoom.objects.create(room_type='USER_SUPPORT')
        room.participants.add(self.user1, self.support_user)
        
        message = ChatMessage.objects.create(
            room=room,
            sender=self.user1,
            content='Hello, I need help!',
            message_type='TEXT'
        )
        
        self.assertEqual(message.content, 'Hello, I need help!')
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.room, room)
        
        # Check that room's last_activity was updated
        room.refresh_from_db()
        self.assertEqual(room.last_activity, message.created_at)
    
    def test_unread_count(self):
        """Test unread message count"""
        room = ChatRoom.objects.create(room_type='USER_SUPPORT')
        room.participants.add(self.user1, self.support_user)
        
        # Create messages
        msg1 = ChatMessage.objects.create(
            room=room,
            sender=self.support_user,
            content='Hello!'
        )
        msg2 = ChatMessage.objects.create(
            room=room, 
            sender=self.support_user,
            content='How can I help?'
        )
        
        # User1 should have 2 unread messages
        self.assertEqual(room.get_unread_count(self.user1), 2)
        
        # Mark first message as read
        membership = ChatRoomMembership.objects.get(room=room, user=self.user1)
        membership.mark_as_read(msg1)
        
        # Should now have 1 unread
        self.assertEqual(room.get_unread_count(self.user1), 1)


class ChatAPITests(APITestCase):
    """Test chat API endpoints"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.support_user = User.objects.create_user(
            username='support',
            email='support@example.com',
            password='testpass123',
            is_staff=True
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_conversations(self):
        """Test getting user conversations"""
        # Create a chat room
        room = ChatRoom.objects.create(
            name='Test Support Chat',
            room_type='USER_SUPPORT'
        )
        room.participants.add(self.user, self.support_user)
        
        response = self.client.get('/api/chat/conversations/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['display_name'], 'Support Agent')
    
    def test_send_message(self):
        """Test sending a message"""
        room = ChatRoom.objects.create(room_type='USER_SUPPORT')
        room.participants.add(self.user, self.support_user)
        
        data = {
            'chat_id': str(room.id),
            'message': 'Hello, I need help!'
        }
        
        response = self.client.post('/api/chat/send-message/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hello, I need help!')
        
        # Verify message was created
        self.assertTrue(
            ChatMessage.objects.filter(
                room=room,
                sender=self.user,
                content='Hello, I need help!'
            ).exists()
        )
    
    def test_get_messages(self):
        """Test getting messages for a room"""
        room = ChatRoom.objects.create(room_type='USER_SUPPORT')
        room.participants.add(self.user, self.support_user)
        
        # Create some messages
        ChatMessage.objects.create(
            room=room,
            sender=self.support_user,
            content='Hello!'
        )
        ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content='Hi, I need help!'
        )
        
        response = self.client.get(f'/api/chat/messages/{room.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_start_support_chat(self):
        """Test starting a support chat"""
        response = self.client.post('/api/chat/support/')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify room was created
        room_id = response.data['id']
        room = ChatRoom.objects.get(id=room_id)
        self.assertEqual(room.room_type, 'USER_SUPPORT')
        self.assertTrue(room.participants.filter(id=self.user.id).exists())
        self.assertTrue(room.participants.filter(id=self.support_user.id).exists())
        
        # Should have a welcome message
        welcome_message = ChatMessage.objects.filter(
            room=room,
            sender=self.support_user
        ).first()
        self.assertIsNotNone(welcome_message)
