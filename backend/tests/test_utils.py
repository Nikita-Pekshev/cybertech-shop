import pytest
from utils import (
    validate_email,
    validate_password,
    hash_password,
    check_password,
    calculate_cart_total,
    generate_order_number,
    is_valid_username
)

# ============================================
# UNIT-ТЕСТЫ: validate_email
# ============================================

class TestValidateEmail:
    def test_valid_emails(self):
        assert validate_email('test@test.com') is True
        assert validate_email('user@domain.ru') is True
        assert validate_email('a@b.com') is True
        assert validate_email('test123@mail.com') is True
    
    def test_invalid_emails(self):
        assert validate_email('') is False
        assert validate_email('test') is False
        assert validate_email('test@') is False
        assert validate_email('@test.com') is False
        assert validate_email('test@test') is False
        assert validate_email(None) is False
    
    def test_edge_cases(self):
        assert validate_email('a@b.c') is True
        assert validate_email('a@b.cd') is True
        assert validate_email('a.b@c.d') is True

# ============================================
# UNIT-ТЕСТЫ: validate_password
# ============================================

class TestValidatePassword:
    def test_valid_passwords(self):
        assert validate_password('123456') is True
        assert validate_password('abcdef') is True
        assert validate_password('a' * 6) is True
    
    def test_invalid_passwords(self):
        assert validate_password('') is False
        assert validate_password('12345') is False
        assert validate_password('abc') is False
        assert validate_password(None) is False

# ============================================
# UNIT-ТЕСТЫ: hash_password и check_password
# ============================================

class TestPasswordHashing:
    def test_hash_password(self):
        hashed = hash_password('123456')
        assert hashed is not None
        assert len(hashed) > 10
    
    def test_check_password_correct(self):
        hashed = hash_password('123456')
        assert check_password('123456', hashed) is True
    
    def test_check_password_incorrect(self):
        hashed = hash_password('123456')
        assert check_password('wrong', hashed) is False
    
    def test_check_password_with_string_hash(self):
        hashed = hash_password('123456')
        assert check_password('123456', hashed) is True

# ============================================
# UNIT-ТЕСТЫ: generate_order_number
# ============================================

class TestGenerateOrderNumber:
    def test_order_number_format(self):
        order_number = generate_order_number(1)
        assert order_number.startswith('ORD-')
        assert len(order_number) > 10
        assert order_number.count('-') == 3
    
    def test_order_number_unique(self):
        order1 = generate_order_number(1)
        order2 = generate_order_number(2)
        assert order1 != order2
    
    def test_order_number_contains_user_id(self):
        order_number = generate_order_number(42)
        assert '-42-' in order_number

# ============================================
# UNIT-ТЕСТЫ: is_valid_username
# ============================================

class TestIsValidUsername:
    def test_valid_usernames(self):
        assert is_valid_username('user') is True
        assert is_valid_username('username123') is True
        assert is_valid_username('user_name') is True
        assert is_valid_username('a' * 20) is True
    
    def test_invalid_usernames(self):
        assert is_valid_username('') is False
        assert is_valid_username('ab') is False
        assert is_valid_username('user@name') is False
        assert is_valid_username('user name') is False
        assert is_valid_username(None) is False

# ============================================
# UNIT-ТЕСТЫ: calculate_cart_total
# ============================================

class TestCalculateCartTotal:
    def test_empty_cart(self):
        assert calculate_cart_total([]) == 0.0
        assert calculate_cart_total(None) == 0.0
    
    def test_single_item(self):
        items = [{'price': 100, 'quantity': 1}]
        assert calculate_cart_total(items) == 100.0
    
    def test_multiple_items(self):
        items = [
            {'price': 100, 'quantity': 2},
            {'price': 50, 'quantity': 3}
        ]
        assert calculate_cart_total(items) == 350.0
    
    def test_items_without_price(self):
        items = [
            {'price': 100, 'quantity': 1},
            {'quantity': 2}
        ]
        assert calculate_cart_total(items) == 100.0