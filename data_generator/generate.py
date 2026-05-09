import json
import uuid
from datetime import datetime, timezone, timedelta
from faker import Faker

fake = Faker("pt_BR")

PLANS = [
    {"planId": "e4aece44-f291-11ec-b939-0242ac120002", "name": "Elite",      "hierarchy": 1},
    {"planId": "2a9b53c8-f292-11ec-b939-0242ac120002", "name": "Specialist", "hierarchy": 2},
    {"planId": "15216afa-f292-11ec-b939-0242ac120002", "name": "Essential",  "hierarchy": 3},
    {"planId": "a1b2c3d4-f292-11ec-b939-0242ac120002", "name": "Light",      "hierarchy": 4},
]

CATEGORY_GROUPS = ["Customer Success", "CX", "Dados", "Liderança", "Vendas"]
EVENT_CATEGORIES = ["masterclass", "especializacao"]
SUBJECTS = ["customer_success", "dados", "cx", "lideranca", "vendas"]


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


# ── Plans ──────────────────────────────────────────────────────────────────────

def generate_plans() -> list[dict]:
    plans = []
    for p in PLANS:
        plans.append({
            "planId": p["planId"],
            "name": p["name"],
            "description": f"Club {p['name']}",
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


# ── Main ───────────────────────────────────────────────────────────────────────

def save(data: list[dict], filename: str) -> None:
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{len(data)} registros gerados em {filename}")

    
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
    
if __name__ == "__main__":
    users     = generate_users(100)
    plans     = generate_plans()
    courses   = generate_courses(50)
    events    = generate_events(30)
    uplans    = generate_userplans(users)
    uprofiles = generate_userprofiles(users)
    audits    = generate_audittraffics(users)
    ucprog    = generate_usercourseprogresses(users, courses)
    ueprog    = generate_newusereventprogresses(users, events, uplans)
    scores    = generate_scores(users, courses)
    ssum      = generate_scoresummarizeds(users, scores)

    save(users,     "users.json")
    save(plans,     "plans.json")
    save(courses,   "courses.json")
    save(events,    "events.json")
    save(uplans,    "userplans.json")
    save(uprofiles, "userprofiles.json")
    save(audits,    "audittraffics.json")
    save(ucprog,    "usercourseprogresses.json")
    save(ueprog,    "newusereventprogresses.json")
    save(scores,    "scores.json")
    save(ssum,      "scoresummarizeds.json")