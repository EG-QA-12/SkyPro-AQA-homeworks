"""API тесты для работы с учителями."""

import pytest
import allure
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock
import requests

from api.teacher_api import TeacherAPI
from data.test_data import VALID_TEACHERS
from data.faker_data import generate_teacher


@allure.epic("SkyPro QA Homework")
@allure.feature("API Tests")
@allure.story("Teacher API Operations")
class TestTeacherAPI:
    """
    Класс для тестирования API учителей.
    
    Тестирует CRUD операции через REST API с использованием моков.
    """
    
    @pytest.fixture
    def teacher_api(self) -> TeacherAPI:
        """
        Фикстура для создания экземпляра TeacherAPI.
        
        Returns:
            TeacherAPI: Экземпляр API клиента
        """
        return TeacherAPI(base_url="http://test-api.local/api/v1")
    
    @allure.title("Тест получения всех учителей")
    @allure.description("Проверка GET запроса для получения списка учителей")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "get", "positive")
    @pytest.mark.api
    def test_get_all_teachers_success(self, teacher_api: TeacherAPI) -> None:
        """
        Тест успешного получения списка всех учителей.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        mock_response_data = [
            {'teacher_id': 1, 'email': 'teacher1@test.com', 'group_id': 100},
            {'teacher_id': 2, 'email': 'teacher2@test.com', 'group_id': 101},
        ]
        
        with allure.step("Выполнить GET запрос для получения списка учителей"):
            with patch.object(teacher_api, 'get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = mock_response_data
                mock_get.return_value = mock_response
                
                result = teacher_api.get_all_teachers()
        
        with allure.step("Проверить результат"):
            assert result == mock_response_data, "Данные учителей не соответствуют ожидаемым"
            assert len(result) == 2, "Количество учителей должно быть 2"
    
    @allure.title("Тест получения учителя по ID")
    @allure.description("Проверка GET запроса для получения конкретного учителя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "get", "positive")
    @pytest.mark.api
    def test_get_teacher_by_id_success(self, teacher_api: TeacherAPI) -> None:
        """
        Тест успешного получения учителя по ID.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_id = 12345
        mock_response_data = {
            'teacher_id': teacher_id,
            'email': 'teacher@test.com',
            'group_id': 100
        }
        
        with allure.step(f"Получить учителя с ID={teacher_id}"):
            with patch.object(teacher_api, 'get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = mock_response_data
                mock_get.return_value = mock_response
                
                result = teacher_api.get_teacher_by_id(teacher_id)
        
        with allure.step("Проверить результат"):
            assert result is not None, "Учитель не должен быть None"
            assert result['teacher_id'] == teacher_id, "ID учителя не совпадает"
            mock_get.assert_called_once_with(f"teachers/{teacher_id}")
    
    @allure.title("Тест получения несуществующего учителя")
    @allure.description("Проверка обработки ошибки при получении несуществующего учителя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "get", "negative")
    @pytest.mark.api
    def test_get_teacher_by_id_not_found(self, teacher_api: TeacherAPI) -> None:
        """
        Тест получения несуществующего учителя.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_id = 999999
        
        with allure.step(f"Попытаться получить учителя с несуществующим ID={teacher_id}"):
            with patch.object(teacher_api, 'get') as mock_get:
                mock_get.side_effect = Exception("Not Found")
                
                result = teacher_api.get_teacher_by_id(teacher_id)
        
        with allure.step("Проверить что возвращен None"):
            assert result is None, "При ошибке должен возвращаться None"
    
    @allure.title("Тест создания учителя")
    @allure.description("Проверка POST запроса для создания нового учителя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "post", "positive")
    @pytest.mark.api
    def test_create_teacher_success(self, teacher_api: TeacherAPI) -> None:
        """
        Тест успешного создания учителя.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_data = generate_teacher()
        mock_response_data = {
            'teacher_id': 12345,
            'email': teacher_data['email'],
            'group_id': teacher_data['group_id']
        }
        
        with allure.step("Создать нового учителя"):
            with patch.object(teacher_api, 'post') as mock_post:
                mock_response = Mock()
                mock_response.json.return_value = mock_response_data
                mock_post.return_value = mock_response
                
                result = teacher_api.create_teacher(teacher_data)
        
        with allure.step("Проверить результат"):
            assert result['email'] == teacher_data['email'], "Email не совпадает"
            assert result['group_id'] == teacher_data['group_id'], "Group ID не совпадает"
            mock_post.assert_called_once_with("teachers", data=teacher_data)
    
    @allure.title("Тест обновления учителя")
    @allure.description("Проверка PUT запроса для обновления данных учителя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "put", "positive")
    @pytest.mark.api
    def test_update_teacher_success(self, teacher_api: TeacherAPI) -> None:
        """
        Тест успешного обновления учителя.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_id = 12345
        update_data = {'email': 'new-email@test.com'}
        mock_response_data = {
            'teacher_id': teacher_id,
            'email': 'new-email@test.com',
            'group_id': 100
        }
        
        with allure.step(f"Обновить учителя с ID={teacher_id}"):
            with patch.object(teacher_api, 'put') as mock_put:
                mock_response = Mock()
                mock_response.json.return_value = mock_response_data
                mock_put.return_value = mock_response
                
                result = teacher_api.update_teacher(teacher_id, update_data)
        
        with allure.step("Проверить результат"):
            assert result['email'] == 'new-email@test.com', "Email не обновлен"
            mock_put.assert_called_once_with(f"teachers/{teacher_id}", data=update_data)
    
    @allure.title("Тест удаления учителя")
    @allure.description("Проверка DELETE запроса для удаления учителя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("api", "delete", "positive")
    @pytest.mark.api
    def test_delete_teacher_success(self, teacher_api: TeacherAPI) -> None:
        """
        Тест успешного удаления учителя.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_id = 12345
        
        with allure.step(f"Удалить учителя с ID={teacher_id}"):
            with patch.object(teacher_api, 'delete') as mock_delete:
                mock_delete.return_value = Mock()
                
                result = teacher_api.delete_teacher(teacher_id)
        
        with allure.step("Проверить результат"):
            assert result is True, "Удаление должно быть успешным"
            mock_delete.assert_called_once_with(f"teachers/{teacher_id}")
    
    @allure.title("Тест удаления несуществующего учителя")
    @allure.description("Проверка обработки ошибки при удалении несуществующего учителя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "delete", "negative")
    @pytest.mark.api
    def test_delete_teacher_not_found(self, teacher_api: TeacherAPI) -> None:
        """
        Тест удаления несуществующего учителя.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_id = 999999
        
        with allure.step(f"Попытаться удалить несуществующего учителя с ID={teacher_id}"):
            with patch.object(teacher_api, 'delete') as mock_delete:
                mock_delete.side_effect = Exception("Not Found")
                
                result = teacher_api.delete_teacher(teacher_id)
        
        with allure.step("Проверить результат"):
            assert result is False, "При ошибке удаления должен возвращаться False"
    
    @allure.title("Тест проверки существования учителя")
    @allure.description("Проверка метода проверки существования учителя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "get", "positive")
    @pytest.mark.api
    def test_teacher_exists_true(self, teacher_api: TeacherAPI) -> None:
        """
        Тест проверки существования учителя.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_id = 12345
        mock_response_data = {
            'teacher_id': teacher_id,
            'email': 'teacher@test.com',
            'group_id': 100
        }
        
        with allure.step(f"Проверить существование учителя с ID={teacher_id}"):
            with patch.object(teacher_api, 'get_teacher_by_id') as mock_get:
                mock_get.return_value = mock_response_data
                
                result = teacher_api.teacher_exists(teacher_id)
        
        with allure.step("Проверить результат"):
            assert result is True, "Учитель должен существовать"
    
    @allure.title("Тест проверки несуществующего учителя")
    @allure.description("Проверка метода проверки несуществующего учителя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "get", "negative")
    @pytest.mark.api
    def test_teacher_exists_false(self, teacher_api: TeacherAPI) -> None:
        """
        Тест проверки несуществующего учителя.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        teacher_id = 999999
        
        with allure.step(f"Проверить существование несуществующего учителя с ID={teacher_id}"):
            with patch.object(teacher_api, 'get_teacher_by_id') as mock_get:
                mock_get.return_value = None
                
                result = teacher_api.teacher_exists(teacher_id)
        
        with allure.step("Проверить результат"):
            assert result is False, "Учитель не должен существовать"
    
    @allure.title("Тест получения учителей по группе")
    @allure.description("Проверка фильтрации учителей по ID группы")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "get", "positive")
    @pytest.mark.api
    def test_get_teachers_by_group(self, teacher_api: TeacherAPI) -> None:
        """
        Тест получения учителей по ID группы.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        group_id = 100
        mock_response_data = [
            {'teacher_id': 1, 'email': 'teacher1@test.com', 'group_id': group_id},
            {'teacher_id': 2, 'email': 'teacher2@test.com', 'group_id': group_id},
        ]
        
        with allure.step(f"Получить учителей группы с ID={group_id}"):
            with patch.object(teacher_api, 'get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = mock_response_data
                mock_get.return_value = mock_response
                
                result = teacher_api.get_teachers_by_group(group_id)
        
        with allure.step("Проверить результат"):
            assert len(result) == 2, "Количество учителей должно быть 2"
            for teacher in result:
                assert teacher['group_id'] == group_id, "ID группы не совпадает"
            mock_get.assert_called_once_with("teachers", params={"group_id": group_id})
    
    @allure.title("Тест поиска учителей по email")
    @allure.description("Проверка поиска учителей по email")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "get", "positive")
    @pytest.mark.api
    def test_search_teachers_by_email(self, teacher_api: TeacherAPI) -> None:
        """
        Тест поиска учителей по email.
        
        Args:
            teacher_api (TeacherAPI): Экземпляр API клиента
        """
        search_email = "teacher@test.com"
        mock_response_data = [
            {'teacher_id': 1, 'email': search_email, 'group_id': 100},
        ]
        
        with allure.step(f"Искать учителей с email={search_email}"):
            with patch.object(teacher_api, 'get') as mock_get:
                mock_response = Mock()
                mock_response.json.return_value = mock_response_data
                mock_get.return_value = mock_response
                
                result = teacher_api.search_teachers_by_email(search_email)
        
        with allure.step("Проверить результат"):
            assert len(result) == 1, "Должен быть найден один учитель"
            assert result[0]['email'] == search_email, "Email не совпадает"
            mock_get.assert_called_once_with("teachers", params={"email": search_email})


@allure.epic("SkyPro QA Homework")
@allure.feature("API Tests")
@allure.story("Base API Client")
class TestBaseAPIClient:
    """
    Класс для тестирования базового API клиента.
    
    Тестирует базовые HTTP методы и управление сессией.
    """
    
    @allure.title("Тест установки токена авторизации")
    @allure.description("Проверка установки Bearer токена")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "auth")
    @pytest.mark.api
    def test_set_auth_token(self) -> None:
        """
        Тест установки токена авторизации.
        """
        from api.base_client import BaseAPIClient
        
        with allure.step("Создать API клиент и установить токен"):
            client = BaseAPIClient("http://test-api.local")
            client.set_auth_token("test-token-12345")
        
        with allure.step("Проверить что токен установлен"):
            assert 'Authorization' in client.session.headers, "Токен не установлен в заголовки"
            assert client.session.headers['Authorization'] == 'Bearer test-token-12345', \
                "Токен установлен некорректно"
    
    @allure.title("Тест очистки токена авторизации")
    @allure.description("Проверка удаления Bearer токена")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("api", "auth")
    @pytest.mark.api
    def test_clear_auth_token(self) -> None:
        """
        Тест очистки токена авторизации.
        """
        from api.base_client import BaseAPIClient
        
        with allure.step("Создать API клиент, установить и очистить токен"):
            client = BaseAPIClient("http://test-api.local")
            client.set_auth_token("test-token-12345")
            client.clear_auth_token()
        
        with allure.step("Проверить что токен удален"):
            assert 'Authorization' not in client.session.headers, \
                "Токен не удален из заголовков"
    
    @allure.title("Тест построения URL")
    @allure.description("Проверка корректного построения URL из base_url и endpoint")
    @allure.severity(allure.severity_level.MINOR)
    @allure.tag("api", "url")
    @pytest.mark.api
    def test_build_url(self) -> None:
        """
        Тест построения URL.
        """
        from api.base_client import BaseAPIClient
        
        with allure.step("Проверить построение URL"):
            client = BaseAPIClient("http://test-api.local/")
            
            # Проверка с ведущим слешем в endpoint
            url1 = client._build_url("/teachers")
            assert url1 == "http://test-api.local/teachers", f"URL построен неверно: {url1}"
            
            # Проверка без ведущего слеша в endpoint
            url2 = client._build_url("teachers")
            assert url2 == "http://test-api.local/teachers", f"URL построен неверно: {url2}"