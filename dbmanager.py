import psycopg2


class DBManager:
    """Класс для работы с данными в БД."""

    def __init__(self, database_name: str, params: dict):
        self.conn = psycopg2.connect(dbname=database_name, **params)
        self.conn.autocommit = True

    def __del__(self):
        self.conn.close()

    def get_companies_and_vacancies_count(self) -> list:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT companies.name, COUNT(vacancies.vacancy_id) as count_vacancies FROM companies
                    INNER JOIN vacancies ON companies.company_id=vacancies.employer_id
                    GROUP BY companies.name
                """)
            data = cur.fetchall()

        return data

    def get_all_vacancies(self) -> list:
        """Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и
        ссылки на вакансию."""
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.salary_to, vacancies.url
                    FROM companies
                    INNER JOIN vacancies ON companies.company_id=vacancies.employer_id
                    ORDER BY companies.name
                """)
            data = cur.fetchall()

        return data

    def get_avg_salary(self) -> float:
        """Получает среднюю зарплату по вакансиям."""
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT AVG(salary_from) as avg_salary FROM vacancies
                """)
            data = cur.fetchone()[0]

        return data

    def get_vacancies_with_higher_salary(self) -> list:
        """Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям."""
        with self.conn.cursor() as cur:
            cur.execute("""
                    SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.url FROM vacancies
                    INNER JOIN companies ON vacancies.employer_id=companies.company_id
                    WHERE vacancies.salary_from > (SELECT AVG(salary_from) FROM vacancies)
                    ORDER BY vacancies.salary_from DESC
                """)
            data = cur.fetchall()

        return data

    def get_vacancies_with_keyword(self, keyword: str) -> list:
        """Получает список всех вакансий, в названии которых содержится переданное в метод слово."""
        with self.conn.cursor() as cur:
            cur.execute(f"""
                    SELECT companies.name, vacancies.name, vacancies.salary_from, vacancies.url FROM vacancies
                    INNER JOIN companies ON vacancies.employer_id=companies.company_id
                    WHERE vacancies.name LIKE '%{keyword}%'
                    ORDER BY vacancies.salary_from DESC
                """)
            data = cur.fetchall()

        return data
