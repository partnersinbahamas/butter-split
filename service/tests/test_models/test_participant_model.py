import pytest

from service.models import User, Participant


@pytest.fixture()
def get_user(db):
    return User.objects.create_user(
        username="some-user",
        first_name="some-first-name",
        last_name="some-last-name",
        password="user-password"
    )

@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    [
        pytest.param('test-participant'),
    ]
)
class TestParticipantModel:
    def test_participant_string_representation(self, get_user: User, name: str):
        participant = Participant.objects.create(name=name, creator=get_user)

        assert str(participant) == name

    def test_participant_should_be_created_with_user(self, get_user: User, name):
        participant = Participant.objects.create(name=name, creator=get_user)

        assert participant.name == name
        assert participant.creator.id == get_user.id

    def test_participant_should_be_created_without_user(self, name):
        participant = Participant.objects.create(name=name)

        assert participant.name == name
        assert participant.creator is None

    def test_participant_should_be_created(self, name):
        Participant.objects.create(name=name)

        assert Participant.objects.count() == 1