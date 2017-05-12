from session import Session, Role
from entry_student import Student
from entry_teacher import Teacher
from entry_class import Class
from entry_schedule import Schedule
from entry_subject import Subject
from colors import Color
from utils import read_date, print_wrong_format, print_wrong_format_

import datetime
import calendar
list_days = ['Воскресенье', 'Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']


def menu_student(session):
    assert session.user_role is Role.STUDENT, 'Role check failed'

    while True:
        print(Color.BLUE, end='')
        print('### Меню ученика ###')
        print('1. Мой класс')
        print('2. Мои оценки')
        print('0. Выход')
        print(Color.RESET, end='')

        option = None
        while option not in ('0', '1', '2'):
            option = input('? ')
        if option is '0':
            break

        if option is '1':
            menu_my_class(session)
        elif option is '2':
            menu_my_marks(session)


def menu_my_class(session):
    student = Student(session, session.student_id)
    my_class = Class(session, student.get(Student.class_id))
    class_teacher = Teacher(session, my_class.id)
    name_middle = class_teacher.get(Teacher.name_middle)
    teacher_phone = class_teacher.get(Teacher.phone)

    while True:
        print(Color.BLUE, end='')
        print('### Мой класс ###')
        print(str(my_class.get(Class.class_number)) + str(my_class.get(Class.class_letter)))

        print('Классный руководитель:', end=' ')
        print(str(class_teacher.get(Teacher.name_last)), end=' ')
        print(str(class_teacher.get(Teacher.name_last)), end=' ')
        if name_middle:
            print(str(name_middle), end=' ')
        if teacher_phone:
            print('[' + str(teacher_phone) + ']', end='')
        print('')

        print('1. Одноклассники')
        print('2. Расписание')
        print('0. Назад')
        print(Color.RESET, end='')

        option = None
        while option not in ('0', '1', '2'):
            option = input('? ')
        if option is '0':
            break

        if option is '1':
            session.db_execute(
                'SELECT student_id FROM students WHERE class_id = %s ORDER BY name_last, name_first, name_middle;',
                my_class.id
            )
            result = session.cursor.fetchall()
            classmates = list(map(lambda x : Student(session, int(x[0])), result))
            for classmate in classmates:
                print(classmate.get(Student.name_last), end=' ')
                print(classmate.get(Student.name_first), end=' ')
                classmate_name_middle = classmate.get(Student.name_middle)
                if classmate_name_middle:
                    print(classmate_name_middle, end=' ')
                classmate_phone = classmate.get(Student.phone)
                if classmate_phone:
                    print('[' + str(classmate_phone) + ']', end='')
                print('')

        elif option is '2':
            print(Color.BLUE, end='')
            print('### Расписание ###')
            for i in range(len(list_days)):
                print(i + 1, '. ', list_days[i], sep='')
            print('0. Назад')
            print(Color.RESET, end='')

            while True:
                option = None
                allowed_options = list('0',) + list(map(lambda x: str(x + 1), range(len(list_days))))
                while option not in allowed_options:
                    option = input('? ')
                if option == '0':
                    break

                option = int(option) - 1
                session.db_execute(
                    'SELECT subject_id, time_begin, time_duration '
                    'FROM schedule WHERE class_id = %s AND day = %s ORDER BY time_begin;',
                    my_class.id, option
                )
                result = session.cursor.fetchall()
                if not result:
                    print('В этот день у Вас нет уроков')
                for row in result:
                    subject_name = Subject(session, int(row[0])).get(Subject.name)
                    time_begin = row[1].strftime('%H:%M')
                    time_end = (datetime.datetime.combine(datetime.date.today(), row[1]) + row[2]).strftime('%H:%M')
                    print(time_begin, '-', time_end, subject_name)


def menu_my_marks(session):
    print(Color.BLUE, end='')
    print('### Мои оценки ###')
    print(Color.RESET, end='')

    session.db_execute('SELECT subject_id, name FROM subjects;')
    subjects = session.cursor.fetchall()
    allowed_options = list('0', ) + list(map(lambda x: str(x + 1), range(len(subjects))))

    print('Выберите предмет:')
    for i in range(len(subjects)):
        print(i + 1, '. ', str(subjects[i][1]), sep='')
    print('0. Назад')
    option = None
    while option not in allowed_options:
        option = input('? ')
    if option is '0':
        return None
    option = int(option) - 1

    print(
        'Выберите период, за который хотите узнать оценки.\n' +
        'Введите начальную и конечную дату в формате ГГГГ-ММ-ДД'
    )
    begin_date = read_date('Введите начальную дату: ')
    end_date = read_date('Введите конечную дату: ') + ' 23:59:59'

    session.db_execute(
        'SELECT value, teacher_id, time '
        'FROM marks '
        'WHERE student_id = %s AND subject_id = %s AND time BETWEEN %s AND %s '
        'ORDER BY time;',
        session.student_id, subjects[option][0], begin_date, end_date
    )
    result = session.cursor.fetchall()
    if not result:
        print('Оценки за указанный период не найдены')
    for row in result:
        teacher = Teacher(session, int(row[1]))
        teacher_name_middle = teacher.get(Teacher.name_middle)

        print('Оценка:', str(row[0]))
        print('Дата:', row[2].date().isoformat(), row[2].time().strftime('%H:%M'))
        print('Учитель:', teacher.get(Teacher.name_last), teacher.get(Teacher.name_first), end=' ')
        if teacher_name_middle:
            print(teacher_name_middle, end='')
        print('\n')