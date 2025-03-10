from django.test import TestCase
from django.contrib.auth.models import User
from .models import Aihealue, Ketju, Vastaus, Notes, Tags


# Tests for the models
class ForumModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='valter', password='test1234')
        self.aihealue = Aihealue.objects.create(header="Django stuff")
        self.ketju = Ketju.objects.create(
            header="How to use Django?",
            content="Can someone help me?",
            author=self.user,
            aihealue=self.aihealue
        )
        self.vastaus = Vastaus.objects.create(
            content="Sure! Here's how...",
            replier=self.user,
            ketju=self.ketju
        )
    # Tests to check the creation of the models
    def test_ketju_creation(self):
        self.assertEqual(self.ketju.header, "How to use Django?")
        self.assertEqual(self.ketju.author.username, "valter")
        self.assertEqual(self.ketju.aihealue.header, "Django stuff")
    # Test to check the related ketju of the vastaus
    def test_vastaus_related_to_ketju(self):
        self.assertEqual(self.vastaus.ketju, self.ketju)
        self.assertEqual(self.vastaus.replier, self.user)


# Tests for the models
class NotesModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='valter', password='test1234')
        self.note = Notes.objects.create(
            owner=self.user,
            header="React tips",
            content="Use components wisely.",
            tags=Tags.REACT
        )
    # Test to check the creation of the Notes model
    def test_note_creation_and_str(self):
        self.assertEqual(self.note.__str__(), "React tips")
        self.assertEqual(self.note.tags, Tags.REACT)
        self.assertEqual(self.note.owner.username, "valter")





from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse


# Tests for the API views
class KetjuAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="valter_api", password="testpass")
        self.aihealue = Aihealue.objects.create(header="Testing area")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    # Tests for POST request
    def test_create_ketju(self):
        url = reverse('ketju-list')  # maps to /api/Ketjut/
        data = {
            'header': 'Test from API',
            'content': 'Creating a Ketju via API test.',
            'author': self.user.id,
            'aihealue': self.aihealue.id
        }
        # Sending a POST request
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['header'], 'Test from API')

    # Tests for GET request
    def test_list_ketjut(self):
        Ketju.objects.create(
            header='Listable Thread',
            content='Testing GET',
            author=self.user,
            aihealue=self.aihealue
        )
        url = reverse('ketju-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Checking if the response contains the created ketju
        self.assertTrue(any(k['header'] == 'Listable Thread' for k in response.data))



# Tests for the API views
class VastausAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="replyuser", password="testpass")
        self.aihealue = Aihealue.objects.create(header="Replies Area")
        self.ketju = Ketju.objects.create(
            header="Thread for reply",
            content="Let's reply here",
            author=self.user,
            aihealue=self.aihealue
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    # Testing if a reply can be created
    def test_create_vastaus(self):
        url = reverse('vastaus-list')  # /api/Vastaukset/
        data = {
            'content': "Here's my reply via API",
            'replier': self.user.id,
            'ketju': self.ketju.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], "Here's my reply via API")


# Tests for the API views
class UnauthenticatedAccessTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="unauth_user", password="testpass")
        self.aihealue = Aihealue.objects.create(header="Restricted")
        self.ketju = Ketju.objects.create(
            header="Auth test thread",
            content="Content",
            author=self.user,
            aihealue=self.aihealue
        )

    def test_unauthenticated_vastaus_post(self):
        url = reverse('vastaus-list')
        data = {
            'content': "Trying to reply without login",
            'replier': self.user.id,
            'ketju': self.ketju.id
        }
        # No authentication
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)



# Tests for the API views
class NotesAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username="user1", password="pass1")
        self.user2 = User.objects.create_user(username="user2", password="pass2")

        # Both users create a note
        Notes.objects.create(
            owner=self.user1,
            header="Note from user1",
            content="Private",
            tags=Tags.PYTHON
        )

        Notes.objects.create(
            owner=self.user2,
            header="Note from user2",
            content="Hidden",
            tags=Tags.REACT
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    # Testing that the notes are user-specific
    def test_notes_are_user_specific(self):
        url = reverse('notes-list')  # /api/Notes/
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(note['owner'] == self.user1.id for note in response.data))
        self.assertFalse(any(note['owner'] == self.user2.id for note in response.data))

