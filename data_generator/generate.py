import json
import uuid
from datetime import datetime, timezone
from faker import Faker

fake = Faker("pt_BR")

def generate_users(n: int = 100) -> list[dict]:
    users = []
    for _ in range(n):
        user_id = str(uuid.uuid4())
        created_at = fake.date_time_between(
            start_date="-2y", end_date="now", tzinfo=timezone.utc
        )
        users.append({
            "userId": user_id,
            "name": fake.first_name(),
            "lastName": fake.last_name(),
            "email": fake.unique.email(),
            "phoneNumber": fake.msisdn(),
            "CSID": f"CS{fake.numerify(text='########')}",
            "active": fake.boolean(chance_of_getting_true=80),
            "profile": fake.random_element(elements=["B2C", "B2B"]),
            "company": fake.company() if fake.boolean(chance_of_getting_true=60) else "",
            "companySize": fake.random_element(
                elements=["1-10", "11-50", "51-200", "201-500", "500+", ""]
            ),
            "acceptedCommunication": fake.boolean(chance_of_getting_true=75),
            "acceptedTerms": True,
            "isForeign": fake.boolean(chance_of_getting_true=5),
            "experienceTime": fake.random_element(
                elements=["Menos de 1 ano", "1-2 anos", "3-5 anos", "Mais de 5 anos", "Não Informado"]
            ),
            "carreerStage": fake.random_element(
                elements=["Iniciante", "Júnior", "Pleno", "Sênior", "Liderança", "Não Informado"]
            ),
            "createdAt": created_at.isoformat(),
        })
    return users


if __name__ == "__main__":
    users = generate_users(100)
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print(f"{len(users)} usuários gerados em users.json")