import argparse
import json
import uuid
from datetime import datetime, timezone, timedelta

from faker import Faker
from google.cloud import storage

fake = Faker("pt_BR")
Faker.seed(42)

PLANS = [
    {"planId": "e4aece44-f291-11ec-b939-0242ac120002", "name": "Master", "hierarchy": 1},
    {"planId": "2a9b53c8-f292-11ec-b939-0242ac120002", "name": "Pro", "hierarchy": 2},
    {"planId": "15216afa-f292-11ec-b939-0242ac120002", "name": "Plus", "hierarchy": 3},
    {"planId": "a1b2c3d4-f292-11ec-b939-0242ac120002", "name": "Starter", "hierarchy": 4},
]

CATEGORY_GROUPS = ["Customer Success", "CX", "Dados", "Liderança", "Vendas"]
EVENT_CATEGORIES = ["masterclass", "especializacao"]
SUBJECTS = ["customer_experience", "dados", "cx", "lideranca", "vendas"]


# ── Upload ──────────────────────────────────────────────────────────────────────

def upload_to_gcs(data: list[dict], collection: str, bucket_name: str) -> None:
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    now = datetime.now(tz=timezone.utc)
    ingest_date = now.strftime("%Y-%m-%d")
    ingest_time = now.strftime("%H%M%S")
    blob_path = f"{collection}/ingest_date={ingest_date}/ingest_time={ingest_time}/data.json"

    blob = bucket.blob(blob_path)
    blob.upload_from_string(
        json.dumps(data, ensure_ascii=False, indent=2),
        content_type="application/json",
    )
    print(f"[OK] {len(data):>6} registros → gs://{bucket_name}/{blob_path}")


# ── Users ──────────────────────────────────────────────────────────────────────

def generate_users(n: int = 100) -> list[dict]:
    users = []
    for _ in range(n):
        created_at = fake.date_time_between(
            start_date="-2y", end_date="now", tzinfo=timezone.utc
        )
        users.append({
            "userId": str(uuid.uuid4()),
            "name": fake.first_name(),
            "lastName": fake.last_name(),
            "email": fake.unique.email(),
            "phoneNumber": fake.msisdn(),
            "LHID": f"LH{fake.numerify(text='########')}",
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


# ── Plans ──────────────────────────────────────────────────────────────────────

def generate_plans() -> list[dict]:
    plans = []
    for p in PLANS:
        plans.append({
            "planId": p["planId"],
            "name": p["name"],
            "description": f"LearnHub {p['name']}",
            "hierarchy": p["hierarchy"],
            "color": fake.hex_color(),
            "trialAvailable": p["hierarchy"] >= 2,
        })
    return plans


# ── Courses ────────────────────────────────────────────────────────────────────

def generate_courses(n: int = 50) -> list[dict]:
    courses = []
    for _ in range(n):
        n_modules = fake.random_int(min=1, max=5)
        modules = []
        for m in range(1, n_modules + 1):
            n_topics = fake.random_int(min=2, max=8)
            topics = [
                {
                    "topicId": str(uuid.uuid4()),
                    "moduleId": str(uuid.uuid4()),
                    "order": t,
                    "title": fake.sentence(nb_words=5).rstrip("."),
                    "durationInSeconds": fake.random_int(min=300, max=3600),
                }
                for t in range(1, n_topics + 1)
            ]
            modules.append({
                "moduleId": str(uuid.uuid4()),
                "order": m,
                "title": fake.sentence(nb_words=4).rstrip("."),
                "summary": fake.paragraph(nb_sentences=2),
                "topics": topics,
            })

        plan_sample = fake.random_elements(
            elements=[p["planId"] for p in PLANS], length=fake.random_int(min=1, max=3), unique=True
        )
        courses.append({
            "courseId": str(uuid.uuid4()),
            "name": fake.sentence(nb_words=4).rstrip("."),
            "description": fake.paragraph(nb_sentences=3),
            "certificate": fake.boolean(chance_of_getting_true=70),
            "categories": [fake.random_element(elements=["CURSOS", "MASTERCLASS"])],
            "categoryGroups": [fake.random_element(elements=CATEGORY_GROUPS)],
            "levels": [str(fake.random_int(min=1, max=3))],
            "tags": fake.words(nb=3),
            "durationHours": fake.random_int(min=1, max=10),
            "durationMinutes": fake.random_int(min=0, max=59),
            "plans": list(plan_sample),
            "modules": modules,
            "createdAt": fake.date_time_between(
                start_date="-3y", end_date="now", tzinfo=timezone.utc
            ).isoformat(),
        })
    return courses


# ── Events ─────────────────────────────────────────────────────────────────────

def generate_events(n: int = 30) -> list[dict]:
    events = []
    for _ in range(n):
        events.append({
            "eventId": str(uuid.uuid4()),
            "title": fake.sentence(nb_words=5).rstrip("."),
            "description": fake.sentence(nb_words=10).rstrip("."),
            "category": fake.random_element(elements=EVENT_CATEGORIES),
            "subject": fake.random_element(elements=SUBJECTS),
            "hostName": fake.name(),
            "hostEmail": fake.email(),
            "highlight": fake.boolean(chance_of_getting_true=20),
            "tags": fake.words(nb=2),
            "durationHours": fake.random_int(min=1, max=3),
            "durationMinutes": fake.random_element(elements=[0, 30]),
        })
    return events


# ── User Plans ─────────────────────────────────────────────────────────────────

def generate_userplans(users: list[dict]) -> list[dict]:
    userplans = []
    for user in users:
        plan = fake.random_element(elements=PLANS)
        is_trial = fake.boolean(chance_of_getting_true=30)
        created_at = datetime.fromisoformat(user["createdAt"])
        validity = created_at + timedelta(days=365 if not is_trial else 7)
        userplans.append({
            "userPlanId": str(uuid.uuid4()),
            "userId": user["userId"],
            "planId": plan["planId"],
            "planName": plan["name"],
            "validity": validity.isoformat(),
            "isTrial": is_trial,
            "trialUsed": is_trial,
            "trialUseDate": created_at.isoformat() if is_trial else None,
            "createdAt": created_at.isoformat(),
            "updatedAt": created_at.isoformat(),
        })
    return userplans


# ── User Profiles ──────────────────────────────────────────────────────────────

def generate_userprofiles(users: list[dict]) -> list[dict]:
    profiles = []
    for user in users:
        profiles.append({
            "userId": user["userId"],
            "personal_data": {
                "about": {
                    "full_name": f"{user['name']} {user['lastName']}",
                    "phone_number": user["phoneNumber"],
                    "goal": fake.sentence(nb_words=8).rstrip("."),
                }
            },
            "professional_data": {
                "career_moment": fake.random_element(
                    elements=["first_job", "transition", "growth", "leadership"]
                ),
                "professional_experience": {
                    "current_role": fake.job(),
                    "company": user.get("company", ""),
                },
            },
            "formation": {
                "academic_formation": {
                    "list": [
                        {
                            "degree": fake.random_element(
                                elements=["Graduação", "Pós-graduação", "MBA", "Mestrado"]
                            ),
                            "course": fake.job(),
                            "institution": fake.company(),
                        }
                    ]
                },
                "skills": {
                    "list": fake.words(nb=5)
                },
            },
        })
    return profiles


# ── Audit Traffics ─────────────────────────────────────────────────────────────

def generate_audittraffics(users: list[dict], n_per_user: int = 5) -> list[dict]:
    routes = [
        {"tag": "login",       "route": "/login"},
        {"tag": "course_view", "route": "/courses"},
        {"tag": "event_view",  "route": "/events"},
        {"tag": "certificate", "route": "/certificates"},
        {"tag": "profile",     "route": "/profile"},
        {"tag": "community",   "route": "/community"},
    ]
    audits = []
    for user in users:
        created_at = datetime.fromisoformat(user["createdAt"])
        for _ in range(fake.random_int(min=1, max=n_per_user)):
            r = fake.random_element(elements=routes)
            audits.append({
                "auditId": str(uuid.uuid4()),
                "userId": user["userId"],
                "tag": r["tag"],
                "route": r["route"],
                "createdAt": fake.date_time_between(
                    start_date=created_at, end_date="now", tzinfo=timezone.utc
                ).isoformat(),
            })
    return audits


# ── User Course Progresses ─────────────────────────────────────────────────────

def generate_usercourseprogresses(users: list[dict], courses: list[dict]) -> list[dict]:
    progresses = []
    for user in users:
        sampled_courses = fake.random_elements(
            elements=courses, length=fake.random_int(min=0, max=5), unique=True
        )
        created_at = datetime.fromisoformat(user["createdAt"])
        for course in sampled_courses:
            for module in course["modules"]:
                for topic in module["topics"]:
                    video_progress = round(fake.pyfloat(min_value=0, max_value=100), 2)
                    progresses.append({
                        "userCourseProgressId": str(uuid.uuid4()),
                        "userId": user["userId"],
                        "courseId": course["courseId"],
                        "moduleId": module["moduleId"],
                        "topicId": topic["topicId"],
                        "durationInSeconds": topic["durationInSeconds"],
                        "progress": round(video_progress / 100 * 10, 2),
                        "videoProgress": video_progress,
                        "lastTopicViewed": fake.boolean(chance_of_getting_true=20),
                        "datesViewed": [
                            fake.date_time_between(
                                start_date=created_at, end_date="now", tzinfo=timezone.utc
                            ).isoformat()
                        ],
                        "createdAt": created_at.isoformat(),
                        "updatedAt": fake.date_time_between(
                            start_date=created_at, end_date="now", tzinfo=timezone.utc
                        ).isoformat(),
                    })
    return progresses


# ── User Event Progresses ──────────────────────────────────────────────────────

def generate_newusereventprogresses(users: list[dict], events: list[dict], userplans: list[dict]) -> list[dict]:
    plan_map = {u["userId"]: u for u in userplans}
    progresses = []
    for user in users:
        sampled_events = fake.random_elements(
            elements=events, length=fake.random_int(min=0, max=3), unique=True
        )
        uplan = plan_map.get(user["userId"], {})
        for event in sampled_events:
            progresses.append({
                "eventProgressId": str(uuid.uuid4()),
                "userId": user["userId"],
                "userEmail": user["email"],
                "userName": f"{user['name']} {user['lastName']}",
                "userPlanId": uplan.get("planId", ""),
                "userPlanName": uplan.get("planName", ""),
                "eventId": event["eventId"],
                "eventName": event["title"],
                "eventCategory": event["category"],
                "eventDate": fake.date_time_between(
                    start_date="-1y", end_date="now", tzinfo=timezone.utc
                ).isoformat(),
                "progress": fake.random_int(min=0, max=100),
            })
    return progresses


# ── Scores ─────────────────────────────────────────────────────────────────────

def generate_scores(users: list[dict], courses: list[dict]) -> list[dict]:
    score_types = {
        1: ("course_started",   10),
        2: ("topic_completed",  5),
        3: ("course_completed", 50),
        4: ("event_attended",   20),
        5: ("comment_posted",   5),
        6: ("login",            2),
        7: ("certificate",      100),
    }
    scores = []
    for user in users:
        created_at = datetime.fromisoformat(user["createdAt"])
        n_scores = fake.random_int(min=1, max=10)
        for _ in range(n_scores):
            type_id, (_, points) = fake.random_element(elements=list(score_types.items()))
            scores.append({
                "scoreId": str(uuid.uuid4()),
                "userId": user["userId"],
                "type": type_id,
                "score": points,
                "active": fake.boolean(chance_of_getting_true=95),
                "entityUniqueIds": [str(uuid.uuid4())],
                "createdAt": fake.date_time_between(
                    start_date=created_at, end_date="now", tzinfo=timezone.utc
                ).isoformat(),
            })
    return scores


# ── Score Summarizeds ──────────────────────────────────────────────────────────

def generate_scoresummarizeds(users: list[dict], scores: list[dict]) -> list[dict]:
    score_map: dict[str, int] = {}
    for s in scores:
        if s["active"]:
            score_map[s["userId"]] = score_map.get(s["userId"], 0) + s["score"]
    return [
        {
            "scoreSummarizedId": str(uuid.uuid4()),
            "userId": user["userId"],
            "score": score_map.get(user["userId"], 0),
            "updatedAt": datetime.now(tz=timezone.utc).isoformat(),
        }
        for user in users
    ]


# ── Subscriptions ──────────────────────────────────────────────────────────────

def generate_subscriptions(users: list[dict], userplans: list[dict]) -> list[dict]:
    plan_map = {u["userId"]: u for u in userplans}
    subscriptions = []
    for user in users:
        uplan = plan_map.get(user["userId"], {})
        created_at = datetime.fromisoformat(user["createdAt"])
        status = fake.random_element(
            elements=["active", "canceled", "suspended", "future"]
        )
        subscriptions.append({
            "subscriptionId": str(uuid.uuid4()),
            "userId": user["userId"],
            "status": status,
            "planId": uplan.get("planId", ""),
            "planName": uplan.get("planName", ""),
            "interval": "months",
            "interval_count": 1,
            "installments": fake.random_element(elements=[1, 6, 12]),
            "start_at": created_at.isoformat(),
            "end_at": (created_at + timedelta(days=365)).isoformat() if status == "canceled" else None,
            "next_billing_at": fake.date_time_between(
                start_date="now", end_date="+1y", tzinfo=timezone.utc
            ).isoformat(),
            "cancel_at": fake.date_time_between(
                start_date=created_at, end_date="now", tzinfo=timezone.utc
            ).isoformat() if status == "canceled" else None,
            "created_at": created_at.isoformat(),
            "updated_at": fake.date_time_between(
                start_date=created_at, end_date="now", tzinfo=timezone.utc
            ).isoformat(),
        })
    return subscriptions


# ── Bills ──────────────────────────────────────────────────────────────────────

def generate_bills(users: list[dict], subscriptions: list[dict]) -> list[dict]:
    sub_map = {s["userId"]: s for s in subscriptions}
    bills = []
    plan_prices = {"Master": 297, "Pro": 197, "Plus": 169, "Starter": 97}
    for user in users:
        sub = sub_map.get(user["userId"], {})
        n_bills = fake.random_int(min=1, max=12)
        created_at = datetime.fromisoformat(user["createdAt"])
        for i in range(n_bills):
            due_at = created_at + timedelta(days=30 * (i + 1))
            status = fake.random_element(elements=["paid", "paid", "paid", "pending", "canceled"])
            amount = plan_prices.get(sub.get("planName", "Plus"), 169)
            bills.append({
                "billId": str(uuid.uuid4()),
                "userId": user["userId"],
                "subscriptionId": sub.get("subscriptionId", ""),
                "amount": float(amount),
                "status": status,
                "installments": sub.get("installments", 1),
                "due_at": due_at.isoformat(),
                "created_at": created_at.isoformat(),
                "updated_at": fake.date_time_between(
                    start_date=created_at, end_date="now", tzinfo=timezone.utc
                ).isoformat(),
            })
    return bills


# ── Consolidated Sales ─────────────────────────────────────────────────────────

def generate_consolidated_sales(users: list[dict], bills: list[dict], userplans: list[dict]) -> list[dict]:
    plan_map = {u["userId"]: u for u in userplans}
    sales = []
    for bill in bills:
        if bill["status"] != "paid":
            continue
        user_id = bill["userId"]
        uplan = plan_map.get(user_id, {})
        sales.append({
            "saleId": str(uuid.uuid4()),
            "bill_id": bill["billId"],
            "UserId": user_id,
            "Status": bill["status"],
            "Vencimento": bill["due_at"],
            "Data_Pagamento": bill["updated_at"],
            "Forma_de_Pagamento": fake.random_element(
                elements=["Cartão de crédito", "Boleto", "Pix"]
            ),
            "Tentativas_Pagamento": fake.random_int(min=1, max=3),
            "Nome_Produto": f"LearnHub {uplan.get('planName', 'Essential')} - Recorrência",
            "Valor": int(bill["amount"]),
            "Valor_Total": int(bill["amount"]) * 12,
            "Plano": uplan.get("planName", "Plus"),
            "Categoria_Produto": uplan.get("planName", "Plus"),
            "Perfil": fake.random_element(elements=["B2C", "B2B"]),
            "Condicao_Pagamento": fake.random_element(
                elements=["Recorrência", "À vista", "Parcelado"]
            ),
            "Numero_Parcelas": bill.get("installments", 1),
            "Tipo_Venda": fake.random_element(
                elements=["Nova Venda", "Ciclo 2 - Rec", "Ciclo 3 - Rec", "Upgrade"]
            ),
            "Usuario_Ativo": fake.boolean(chance_of_getting_true=80),
            "Data_Atualizacao": bill["updated_at"],
        })
    return sales


# ── Comments ───────────────────────────────────────────────────────────────────

def generate_comments(users: list[dict], userplans: list[dict], n: int = 80) -> list[dict]:
    plan_map = {u["userId"]: u for u in userplans}
    comments = []
    for _ in range(n):
        user = fake.random_element(elements=users)
        uplan = plan_map.get(user["userId"], {})
        comments.append({
            "commentId": str(uuid.uuid4()),
            "userId": user["userId"],
            "userName": f"{user['name']} {user['lastName']}",
            "userEmail": user["email"],
            "planId": uplan.get("planId", ""),
            "postId": str(uuid.uuid4()),
            "parentCommentId": None,
            "comment": fake.paragraph(nb_sentences=2),
            "likes": fake.random_int(min=0, max=50),
            "totalComments": fake.random_int(min=0, max=10),
            "createdAt": fake.date_time_between(
                start_date="-1y", end_date="now", tzinfo=timezone.utc
            ).isoformat(),
        })
    return comments


# ── Likes ──────────────────────────────────────────────────────────────────────

def generate_likes(users: list[dict], comments: list[dict], n: int = 150) -> list[dict]:
    likes = []
    for _ in range(n):
        user = fake.random_element(elements=users)
        comment = fake.random_element(elements=comments)
        likes.append({
            "likeId": str(uuid.uuid4()),
            "userId": user["userId"],
            "postId": comment["postId"],
            "commentId": comment["commentId"],
            "createdAt": fake.date_time_between(
                start_date="-1y", end_date="now", tzinfo=timezone.utc
            ).isoformat(),
        })
    return likes


# ── Certificates ───────────────────────────────────────────────────────────────

def generate_certificates(users: list[dict], courses: list[dict]) -> list[dict]:
    certificates = []
    for user in users:
        eligible = [c for c in courses if c["certificate"]]
        sampled = fake.random_elements(
            elements=eligible, length=fake.random_int(min=0, max=3), unique=True
        )
        for course in sampled:
            certificates.append({
                "certificateId": str(uuid.uuid4()),
                "userId": user["userId"],
                "userName": f"{user['name']} {user['lastName']}",
                "courseId": course["courseId"],
                "courseName": course["name"],
                "finalProgress": round(fake.pyfloat(min_value=90, max_value=100), 2),
                "durationHours": course["durationHours"],
                "durationMinutes": course["durationMinutes"],
                "fileName": f"{user['name']}--{course['name'].replace(' ', '')}--{str(uuid.uuid4())}.pdf",
                "finishDate": fake.date_time_between(
                    start_date="-1y", end_date="now", tzinfo=timezone.utc
                ).isoformat(),
            })
    return certificates


# ── Aprovados Especializacao ───────────────────────────────────────────────────

def generate_specialization_graduates(users: list[dict], events: list[dict], userplans: list[dict]) -> list[dict]:
    plan_map = {u["userId"]: u for u in userplans}
    especializacoes = [e for e in events if e["category"] == "especializacao"]
    aprovados = []
    for user in users:
        if not especializacoes:
            break
        if not fake.boolean(chance_of_getting_true=30):
            continue
        event = fake.random_element(elements=especializacoes)
        uplan = plan_map.get(user["userId"], {})
        aprovados.append({
            "aprovadoId": str(uuid.uuid4()),
            "userId": user["userId"],
            "userEmail": user["email"],
            "userName": f"{user['name']} {user['lastName']}",
            "userPlanName": uplan.get("planName", ""),
            "eventId": event["eventId"],
            "eventTitle": event["title"],
            "average_progress": round(fake.pyfloat(min_value=75, max_value=100), 2),
            "start_time": fake.date_time_between(
                start_date="-1y", end_date="now", tzinfo=timezone.utc
            ).isoformat(),
        })
    return aprovados


# ── Customers Vindi ────────────────────────────────────────────────────────────

def generate_gateway_customers(users: list[dict]) -> list[dict]:
    customers = []
    for user in users:
        customers.append({
            "customerId": str(uuid.uuid4()),
            "userId": user["userId"],
            "name": f"{user['name']} {user['lastName']}",
            "email": user["email"],
            "registry_code": fake.cpf(),
            "status": "active" if user["active"] else "inactive",
            "address": {
                "street": fake.street_name(),
                "number": fake.building_number(),
                "zipcode": fake.postcode(),
                "city": fake.city(),
                "state": fake.estado_sigla(),
                "country": "BR",
            },
            "phones": [{"phone_type": "mobile", "number": user["phoneNumber"]}],
            "created_at": user["createdAt"],
        })
    return customers


# ── HubSpot Contacts ───────────────────────────────────────────────────────────

def generate_crm_contacts(users: list[dict], userplans: list[dict]) -> list[dict]:
    plan_map = {u["userId"]: u for u in userplans}
    contacts = []
    for user in users:
        uplan = plan_map.get(user["userId"], {})
        is_trial = uplan.get("isTrial", False)
        trial_cancel = fake.boolean(chance_of_getting_true=40) if is_trial else None
        contacts.append({
            "hubspot_id": str(fake.random_int(min=10000000, max=99999999)),
            "email": user["email"],
            "firstname": user["name"],
            "lastname": user["lastName"],
            "phone": user["phoneNumber"],
            "company": user.get("company") or None,
            "jobtitle": fake.job() if fake.boolean(chance_of_getting_true=60) else None,
            "perfil_do_lead": user["profile"],
            "seu_cargo": fake.random_element(
                elements=["CS", "CX", "Liderança", "Analista", "Buscando Recolocação", None]
            ),
            "tamanho_da_empresa": user.get("companySize") or None,
            "hubspot_owner_id": str(fake.random_int(min=100, max=999)) if fake.boolean(chance_of_getting_true=50) else None,
            "userid": user["userId"],
            "data_inicio_trial": uplan.get("trialUseDate") if is_trial else None,
            "trial_cancel": trial_cancel,
            "trial_cancel_date": fake.date_time_between(
                start_date="-6m", end_date="now", tzinfo=timezone.utc
            ).isoformat() if trial_cancel else None,
            "trial_business": fake.sentence(nb_words=5) if (trial_cancel and user["profile"] == "B2B") else None,
            "trial_user": fake.sentence(nb_words=5) if (trial_cancel and user["profile"] == "B2C") else None,
            "lastmodifieddate": fake.date_time_between(
                start_date="-30d", end_date="now", tzinfo=timezone.utc
            ).isoformat(),
            "_ingest_date": datetime.now(tz=timezone.utc).date().isoformat(),
            "_source": "hubspot",
        })
    return contacts


# ── User Course Progress Summarizeds ───────────────────────────────────────────

def generate_usercourseprogresssummarizeds(users: list[dict], userplans: list[dict], ucprog: list[dict]) -> list[dict]:
    plan_map = {u["userId"]: u for u in userplans}
    prog_map: dict[str, list] = {}
    for p in ucprog:
        prog_map.setdefault(p["userId"], []).append(p)

    summarizeds = []
    for user in users:
        uplan = plan_map.get(user["userId"], {})
        progs = prog_map.get(user["userId"], [])
        total_minutes = round(sum(p["durationInSeconds"] for p in progs) / 60, 2)
        created_at = datetime.fromisoformat(user["createdAt"])
        summarizeds.append({
            "userId": user["userId"],
            "userName": f"{user['name']} {user['lastName']}",
            "company": user.get("company", ""),
            "planName": uplan.get("planName", ""),
            "courses": list({p["courseId"] for p in progs}),
            "events": [],
            "totalWatchedTimeInMinutes": total_minutes,
            "totalWatchedTimeCurrentMonthInMinutes": round(total_minutes * 0.3, 2),
            "userSince": created_at.isoformat(),
            "updatedAt": datetime.now(tz=timezone.utc).isoformat(),
        })
    return summarizeds


# ── Entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LearnHub synthetic data generator")
    parser.add_argument("--bucket",  default="edtech-generator-dev", help="GCS bucket de destino")
    parser.add_argument("--users",   type=int, default=100,  help="Número de usuários")
    parser.add_argument("--courses", type=int, default=50,   help="Número de cursos")
    parser.add_argument("--events",  type=int, default=30,   help="Número de eventos")
    args = parser.parse_args()

    BUCKET = args.bucket

    print(f"\n{'='*55}")
    print(f"  LearnHub Data Generator")
    print(f"  Bucket : gs://{BUCKET}")
    print(f"  Users  : {args.users} | Courses: {args.courses} | Events: {args.events}")
    print(f"{'='*55}\n")

    # ── Geração (dependências respeitadas) ──────────────────
    users      = generate_users(args.users)
    plans      = generate_plans()
    courses    = generate_courses(args.courses)
    events     = generate_events(args.events)
    uplans     = generate_userplans(users)
    uprofile   = generate_userprofiles(users)
    audits     = generate_audittraffics(users)
    ucprog     = generate_usercourseprogresses(users, courses)
    ueprog     = generate_newusereventprogresses(users, events, uplans)
    scores     = generate_scores(users, courses)
    ssum       = generate_scoresummarizeds(users, scores)
    ucprog_sum = generate_usercourseprogresssummarizeds(users, uplans, ucprog)
    subs       = generate_subscriptions(users, uplans)
    bills      = generate_bills(users, subs)
    sales      = generate_consolidated_sales(users, bills, uplans)
    comments   = generate_comments(users, uplans)
    likes      = generate_likes(users, comments)
    certs      = generate_certificates(users, courses)
    aprovs     = generate_specialization_graduates(users, events, uplans)
    vindi      = generate_gateway_customers(users)
    hubspot    = generate_crm_contacts(users, uplans)

    # ── Upload para GCS ─────────────────────────────────────
    upload_to_gcs(users,      "users",                          BUCKET)
    upload_to_gcs(plans,      "plans",                          BUCKET)
    upload_to_gcs(courses,    "courses",                        BUCKET)
    upload_to_gcs(events,     "events",                         BUCKET)
    upload_to_gcs(uplans,     "userplans",                      BUCKET)
    upload_to_gcs(uprofile,   "userprofiles",                   BUCKET)
    upload_to_gcs(audits,     "audittraffics",                  BUCKET)
    upload_to_gcs(ucprog,     "usercourseprogresses",           BUCKET)
    upload_to_gcs(ueprog,     "newusereventprogresses",         BUCKET)
    upload_to_gcs(ucprog_sum, "usercourseprogresssummarizeds",  BUCKET)
    upload_to_gcs(scores,     "scores",                         BUCKET)
    upload_to_gcs(ssum,       "scoresummarizeds",               BUCKET)
    upload_to_gcs(subs,       "subscriptions",                  BUCKET)
    upload_to_gcs(bills,      "bills",                          BUCKET)
    upload_to_gcs(sales,      "consolidated_sales",             BUCKET)
    upload_to_gcs(comments,   "comments",                       BUCKET)
    upload_to_gcs(likes,      "likes",                          BUCKET)
    upload_to_gcs(certs,      "certificates",                   BUCKET)
    upload_to_gcs(aprovs,     "specialization_graduates",       BUCKET)
    upload_to_gcs(vindi,      "gateway_customers",              BUCKET)
    upload_to_gcs(hubspot,    "crm_contacts",                   BUCKET)

    print(f"\n{'='*55}")
    print(f"  Geração concluída — 21 collections no GCS")
    print(f"{'='*55}\n")