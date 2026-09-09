import tempfile
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from users_app.models import Profile


User = get_user_model()


class ProfileImageUploadTests(APITestCase):
    """Test profile image uploads and their timestamps."""

    @classmethod
    def setUpClass(cls):
        """Create temporary storage for uploaded test images."""
        super().setUpClass()
        cls.media_directory = tempfile.TemporaryDirectory()
        cls.media_override = override_settings(
            MEDIA_ROOT=cls.media_directory.name,
        )
        cls.media_override.enable()

    @classmethod
    def tearDownClass(cls):
        """Remove uploaded test images after all tests."""
        cls.media_override.disable()
        cls.media_directory.cleanup()
        super().tearDownClass()

    def setUp(self):
        """Create and authenticate a customer profile."""
        self.user = self._create_user()
        self.profile = Profile.objects.create(
            user=self.user,
            type=Profile.UserType.CUSTOMER,
        )
        self._authenticate()
        self.url = f"/api/profile/{self.user.pk}/"

    def _create_user(self):
        """Create a user for the image upload tests."""
        return User.objects.create_user(
            username="imageuser",
            email="imageuser@example.com",
            password="S3cure-Pass!482",
        )

    def _authenticate(self):
        """Authenticate the API client with a token."""
        token = Token.objects.create(user=self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {token.key}"
        )

    def _create_image(self):
        """Create a valid in-memory PNG image."""
        image_data = BytesIO()
        Image.new("RGB", (1, 1)).save(image_data, format="PNG")
        image_data.seek(0)
        return SimpleUploadedFile(
            "profile.png",
            image_data.read(),
            content_type="image/png",
        )

    def test_customer_image_upload_sets_uploaded_at(self):
        """Store a timestamp when a customer uploads an image."""
        image = self._create_image()
        response = self._upload(image)
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.profile.file.name)
        self.assertIsNotNone(self.profile.uploaded_at)

    def test_business_profile_can_upload_image(self):
        """Allow a business profile to upload an image too."""
        self.profile.type = Profile.UserType.BUSINESS
        self.profile.save(update_fields=["type"])
        response = self._upload(self._create_image())
        self.profile.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(self.profile.uploaded_at)

    def _upload(self, image):
        """Upload an image through the profile endpoint."""
        return self.client.patch(
            self.url,
            {"file": image},
            format="multipart",
        )
