from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Aihealue, Ketju, Vastaus, Notes, Tags

User = get_user_model()


# Forum mallien testit
class ForumModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='Teppo',
            email='testaaja@example.com',
            password='test1234'
        )
        self.aihealue = Aihealue.objects.create(header="Python")
        self.ketju = Ketju.objects.create(
            header="Testi kysymys?",
            content="Can someone help me?",
            author=self.user,
            aihealue=self.aihealue
        )
        self.vastaus = Vastaus.objects.create(
            content="Yep näin",
            replier=self.user,
            ketju=self.ketju
        )

    def test_ketju_creation(self):
        self.assertEqual(self.ketju.header, "Testi kysymys?")
        self.assertEqual(self.ketju.author.username, "Teppo")
        self.assertEqual(self.ketju.aihealue.header, "Python")

    def test_vastaus_related_to_ketju(self):
        self.assertEqual(self.vastaus.ketju, self.ketju)
        self.assertEqual(self.vastaus.replier, self.user)


# Muistiinpanojen testit
class NotesModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='Teppo',
            email='testaaja@example.com',
            password='test1234'
        )
        self.note = Notes.objects.create(
            owner=self.user,
            header="React",
            content="Komponentit",
            tags=Tags.REACT
        )

    def test_note_creation_and_str(self):
        self.assertEqual(str(self.note), "React")
        self.assertEqual(self.note.tags, Tags.REACT)
        self.assertEqual(self.note.owner.username, "Teppo")


from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse


# API Testit, Ketju (Thread)
class KetjuAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testaaja_api",
            email="testaaja_api@example.com",
            password="testpass"
        )
        self.aihealue = Aihealue.objects.create(header="Testing")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_ketju(self):
        url = reverse('ketju-list')
        data = {
            'header': 'API testi',
            'content': 'Luo ketju API testin kautta',
            'author': self.user.id,
            'aihealue': self.aihealue.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['header'], 'API testi')

    def test_list_ketjut(self):
        Ketju.objects.create(
            header='Luettelo',
            content='Testaa GET',
            author=self.user,
            aihealue=self.aihealue
        )
        url = reverse('ketju-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(k['header'] == 'Luettelo' for k in response.data))


# API Testit,Vastaus (Reply)
class VastausAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="replyuser",
            email="reply@example.com",
            password="testpass"
        )
        self.aihealue = Aihealue.objects.create(header="Vastaukset")
        self.ketju = Ketju.objects.create(
            header="Vastaus ketju",
            content="Vastaus",
            author=self.user,
            aihealue=self.aihealue
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_vastaus(self):
        url = reverse('vastaus-list')
        data = {
            'content': "Vastaus APIn kautta",
            'replier': self.user.id,
            'ketju': self.ketju.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], "Vastaus APIn kautta")


# Testi jos ei ole kirjautunut
class UnauthenticatedAccessTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="unauth_user",
            email="unauth@example.com",
            password="testpass"
        )
        self.aihealue = Aihealue.objects.create(header="Restricted")
        self.ketju = Ketju.objects.create(
            header="Testi kejua",
            content="Testaa",
            author=self.user,
            aihealue=self.aihealue
        )

    def test_unauthenticated_vastaus_post(self):
        url = reverse('vastaus-list')
        data = {
            'content': "Yritetään vastata ilman kirjautumista",
            'replier': self.user.id,
            'ketju': self.ketju.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)


# Käyttäjän muistiot
class NotesAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="Teppo1",
            email="Teppo1@example.com",
            password="pass1"
        )
        self.user2 = User.objects.create_user(
            username="Tero2",
            email="Tero2@example.com",
            password="pass2"
        )

        Notes.objects.create(
            owner=self.user1,
            header="Teppo muistio",
            content="Private",
            tags=Tags.PYTHON
        )
        Notes.objects.create(
            owner=self.user2,
            header="Teppo muistio 2",
            content="Hidden",
            tags=Tags.REACT
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user1)

    def test_notes_are_user_specific(self):
        url = reverse('notes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(all(note['owner'] == self.user1.id for note in response.data))
        self.assertFalse(any(note['owner'] == self.user2.id for note in response.data))
