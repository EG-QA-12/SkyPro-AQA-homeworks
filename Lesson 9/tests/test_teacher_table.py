"""Тесты для проверки операций с таблицей учителей через бизнес-логику (db)."""

import pytest
from test_data import INVALID_EMAILS, INVALID_IDS
from faker_data import generate_teacher


@pytest.fixture
def db():
    from db import get_db_connection

    return get_db_connection()


@pytest.fixture(autouse=True)
def cleanup(db):
    yield
    # Очистка всех учителей после каждого теста
    for teacher in db.get_teacher():
        db.delete(teacher[0])


@pytest.mark.parametrize('teacher', [generate_teacher() for _ in range(3)])
def test_add_teacher(db, teacher):
    db.add_teacher(
        teacher_id=teacher['teacher_id'],
        email=teacher['email'],
        group_id=teacher['group_id']
    )
    teachers = db.get_teacher()
    assert (teacher['teacher_id'], teacher['email'], teacher['group_id']) in teachers
    db.delete(teacher['teacher_id'])


@pytest.mark.parametrize('invalid_id', INVALID_IDS)
def test_add_teacher_invalid_id(db, invalid_id):
    t = generate_teacher()
    with pytest.raises(ValueError):
        db.add_teacher(teacher_id=invalid_id, email=t['email'], group_id=t['group_id'])


@pytest.mark.parametrize('invalid_email', INVALID_EMAILS)
def test_add_teacher_invalid_email(db, invalid_email):
    t = generate_teacher()
    with pytest.raises(ValueError):
        db.add_teacher(teacher_id=t['teacher_id'], email=invalid_email, group_id=t['group_id'])


@pytest.mark.parametrize('invalid_group_id', [None, 0, -1, -100, 'abc'])
def test_add_teacher_invalid_group_id(db, invalid_group_id):
    t = generate_teacher()
    with pytest.raises(ValueError):
        db.add_teacher(teacher_id=t['teacher_id'], email=t['email'], group_id=invalid_group_id)


def test_update_teacher(db):
    t = generate_teacher()
    db.add_teacher(
        teacher_id=t['teacher_id'],
        email=t['email'],
        group_id=t['group_id']
    )
    new_email = 'new_' + t['email']
    db.update_teacher(teacher_id=t['teacher_id'], new_email=new_email)
    teachers = db.get_teacher()
    assert (t['teacher_id'], new_email, t['group_id']) in teachers
    db.delete(t['teacher_id'])


def test_delete_teacher(db):
    t = generate_teacher()
    db.add_teacher(
        teacher_id=t['teacher_id'],
        email=t['email'],
        group_id=t['group_id']
    )
    db.delete(t['teacher_id'])
    teachers = db.get_teacher()
    assert (t['teacher_id'], t['email'], t['group_id']) not in teachers


def test_update_nonexistent_teacher(db):
    with pytest.raises(ValueError):
        db.update_teacher(teacher_id=999999, new_email='notfound@mail.com')


def test_delete_nonexistent_teacher(db):
    with pytest.raises(ValueError):
        db.delete(999999)


def test_empty_table(db):
    teachers = db.get_teacher()
    assert isinstance(teachers, list)
    # либо пусто, либо только кортежи
    assert len(teachers) == 0 or all(isinstance(t, tuple) for t in teachers)
