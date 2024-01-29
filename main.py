from config import config
from dbmanager import DBManager
from utils import get_hh_data, create_database, save_data_to_database


def main():

    employers_ids = [
        '1740',
        '1455',
        '9108862',
        '1709087',
        '4968248',
        '9106965',
        '10295896',
        '9035038',
        '9498120',
        '10672297'
    ]
    database_name = 'hh_database'
    params = config()

    data = get_hh_data(employers_ids)
    create_database(database_name, params)
    save_data_to_database(data, database_name, params)
    database_manager = DBManager(database_name, params)

    while True:
        user_input = input("""
        Пожалуйста, выберите одно из следующих действий и введите соответствующую цифру:
        1 - список всех компаний и количество вакансий у каждой компании;
        2 - список всех вакансий с указанием названия компании, названия вакансии и зарплаты и
        ссылки на вакансию;
        3 - среднюю зарплату по вакансиям;
        4 - список всех вакансий, у которых зарплата выше средней по всем вакансиям;
        5 - список всех вакансий, в названии которых содержится переданное в метод слово.
        """)

        if user_input in ['1', '2', '3', '4', '5']:

            if user_input == '1':
                companies = database_manager.get_companies_and_vacancies_count()
                for company in companies:
                    print(f"{company[0]} - {company[1]}")
                    print('')
            elif user_input == '2':
                vacancies = database_manager.get_all_vacancies()
                for vacancy in vacancies:
                    print(f"{vacancy[0]}: {vacancy[1]}\n"
                          f"зарплата: от {vacancy[2]} до {vacancy[3]}\n"
                          f"ссылка: {vacancy[4]}\n")
                    print('')
            elif user_input == '3':
                avg_salary = database_manager.get_avg_salary()
                print(round(avg_salary))
            elif user_input == '4':
                more_avg_salary = database_manager.get_vacancies_with_higher_salary()
                for vacancy in more_avg_salary:
                    print(f"{vacancy[0]}: {vacancy[1]}\n"
                          f"зарплата: от {vacancy[2]}\n"
                          f"ссылка: {vacancy[3]}\n")
                    print('')
            elif user_input == '5':
                keyword = input("Введите слово, содержащееся в названии вакансии:\n")
                vacancies_with_keyword = database_manager.get_vacancies_with_keyword(keyword)
                for vacancy in vacancies_with_keyword:
                    print(f"{vacancy[0]}: {vacancy[1]}\n"
                          f"зарплата: от {vacancy[2]}\n"
                          f"ссылка: {vacancy[3]}\n")
                    print('')
        else:
            print("Такого действия не существует. Выберите правильное действие снова.")


if __name__ == '__main__':
    main()
