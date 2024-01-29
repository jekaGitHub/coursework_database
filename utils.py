from typing import Any

import psycopg2
import requests


def get_hh_data(employers_ids: list[str]) -> list[dict[str, Any]]:
    """Получить данные о работодателях и их вакансиях с сайта hh.ru с помощью API."""

    data = []
    vacancies = []
    url = 'https://api.hh.ru/'

    for employer_id in employers_ids:
        employer_data = requests.get(f'{url}employers/{employer_id}').json()
        vacancies_data = requests.get(f'{url}vacancies', params={'employer_id': employer_id, 'only_with_salary': True}).json()

        for vacancy in vacancies_data['items']:
            vacancies.append({
                'id': vacancy['id'],
                'name': vacancy['name'],
                'description': vacancy['snippet']['responsibility'],
                'salary_from': int(vacancy['salary']['from'] if vacancy['salary']['from'] is not None else 'Нет данных'),
                'salary_to': int(vacancy['salary']['to'] if vacancy['salary']['to'] is not None else 'Нет данных'),
                'currency': vacancy['salary']['currency'],
                'city': vacancy['area']['name'],
                'url': vacancy['alternate_url']
            })

        data.append({
            "employer": {
                'id': employer_data['id'],
                'name': employer_data['name'],
                'city': employer_data['area']['name'],
                'description': employer_data['description'],
                'url': employer_data['alternate_url']
            },
            "vacancies": vacancies
        })

    return data


def create_database(database_name: str, params: dict) -> None:
    """Создание базы данных и таблиц для сохранения данных о работодателях и их вакансиях."""

    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(f"CREATE DATABASE {database_name}")
    except psycopg2.errors.DuplicateDatabase:
        cur.execute(f"DROP DATABASE {database_name}")
        cur.execute(f"CREATE DATABASE {database_name}")

    conn.close()

    conn = psycopg2.connect(dbname=database_name, **params)
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE companies (
                company_id SERIAL PRIMARY KEY,
                external_id VARCHAR NOT NULL,
                name VARCHAR(255) NOT NULL,
                city VARCHAR(255),
                description TEXT,
                url TEXT
            )
        """)

    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                employer_id INT REFERENCES companies(company_id),
                external_id VARCHAR NOT NULL,
                name VARCHAR NOT NULL,
                description TEXT,
                salary_from INT,
                salary_to INT,
                currency VARCHAR,
                city VARCHAR(255),
                url TEXT
            )
        """)

    conn.commit()
    conn.close()


def save_data_to_database(data: list[dict[str, Any]], database_name: str, params: dict) -> None:
    """Заполнение таблиц данными о работодателях и их вакансиях."""

    conn = psycopg2.connect(dbname=database_name, **params)

    with conn.cursor() as cur:
        for item in data:
            employer_data = item['employer']
            cur.execute(
                """
                INSERT INTO companies (external_id, name, city, description, url)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING company_id
                """,
                (employer_data['id'], employer_data['name'], employer_data['city'], employer_data['description'],
                 employer_data['url'])
            )
            company_id = cur.fetchone()[0]

            vacancies_data = item['vacancies']
            for vacancy in vacancies_data:
                cur.execute(
                    """
                    INSERT INTO vacancies (employer_id, external_id, name, description, salary_from, salary_to,
                    currency, city, url)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (company_id, vacancy['id'], vacancy['name'], vacancy['description'],
                     vacancy['salary_from'], vacancy['salary_to'], vacancy['currency'], vacancy['city'], vacancy['url'])
                )

    conn.commit()
    conn.close()
