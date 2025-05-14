#JWT testit Jani

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTTokenTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@gmail.com',
            password='testpassword'
        )
        self.login_url = "/api/login/"
        self.protected_url = "/api/protected-view/"  # Vaihda oikeaksi endpointiksi

    def test_obtain_token(self):
        response = self.client.post(self.login_url, {
            "email": "testuser@gmail.com",
            "password": "testpassword"
        })
        print("Login response status:", response.status_code)
        print("Login cookies:", response.cookies)

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)  # Varmista että access-token on cookieissa

def test_access_protected_view(self):
    login_response = self.client.post(self.login_url, {
        "email": "testuser@gmail.com",
        "password": "testpassword"
    })
    self.assertEqual(login_response.status_code, 200)

    # Get the access token from the cookies and set it in the request
    access_token = login_response.cookies['access_token'].value
    self.client.cookies['access_token'] = access_token

    # Make the protected view request with the token in cookies
    response = self.client.get(self.protected_url)

    print("Protected response:", response.status_code)
    self.assertEqual(response.status_code, 200)

    def test_refresh_token(self):
        # Kirjaudu ensin saadaksesi refresh-tokenin evästeisiin
        login_response = self.client.post(self.login_url, {
            "email": "testuser@gmail.com",
            "password": "testpassword"
        })
        self.assertEqual(login_response.status_code, 200)

        # Oleta että refresh-token on nimeltään 'refresh'
        response = self.client.post("/api/refresh/")  # SimpleJWT tukee cookien käyttöä
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)  # Uusi access-token saatu
