# CarConnect: Dealership Reviews and Sentiment Analysis

A full-stack capstone application built from the IBM Developer Skills Network
starter. React provides dealer search, registration and reviews; Django manages
sessions, car makes/models and the admin; Express stores dealer/review records
in MongoDB; a Flask service analyzes text with NLTK VADER.

## Run in the course lab

```bash
git clone https://github.com/jatinmahire/xrwvm-fullstack_developer_capstone.git
cd xrwvm-fullstack_developer_capstone
bash bin/start-lab.sh
```

Open the lab's port 8000 preview. Express is exposed on port 3030 and sentiment
on 5050. Demo credentials are generated into the ignored `.env` file; obtain
them locally from that file. They are disposable lab accounts, not real users.
The starter's dealership/review/car data are educational examples.

## Services and endpoints

| Service | Endpoints |
|---|---|
| Django/React | `/`, `/login`, `/register`, `/dealer/15`, `/postreview/15` |
| Authentication | `/djangoapp/login`, `/djangoapp/logout`, `/djangoapp/register` |
| Django API | `/djangoapp/get_dealers`, `/djangoapp/get_dealers/Kansas`, `/djangoapp/dealer/15`, `/djangoapp/reviews/dealer/15`, `/djangoapp/get_cars` |
| Express/Mongo | `/fetchDealers`, `/fetchDealers/Kansas`, `/fetchDealer/15`, `/fetchReviews/dealer/15` |
| Sentiment | `/analyze/Fantastic%20services` |
| Administration | `/admin/` |

`bin/deploy-kubernetes.sh` builds and pushes service images to the learner's
IBM container registry namespace and deploys only the named CarConnect
resources. `bin/capture-outputs.py` saves actual cURL output for the submission.
Use the application origin and API URLs for the running deployment.

## Validation

GitHub Actions installs dependencies, builds React, starts MongoDB-backed
Express and Flask services, runs Django checks and unit/integration tests, and
builds the Django container. Capture the actual successful run for submission.
Run locally with `cd server && python manage.py test --verbosity 2` once the
backend services are available. No successful execution is claimed by this
README alone.

## Notes

The application uses CSRF-protected session authentication, validates review
input and populates seed data idempotently without deleting posted reviews.
This educational deployment uses SQLite for Django and a single MongoDB
instance. It is not a production HA setup; use managed persistent databases,
TLS, rate limiting, backups and secret management for a production service.
Team profiles on About are fictional demonstration profiles.

Starter: https://github.com/ibm-developer-skills-network/xrwvm-fullstack_developer_capstone
License: Apache-2.0. AI assistance was used to prepare this implementation.
