import boto3
from botocore.exceptions import ClientError
from typing import Optional, List
from app.schemas.cart import CartItemInDB
from app.schemas.user import UserInDB
from app.schemas.product import Product

class AWSClient:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.cognito = boto3.client('cognito-idp')
        self.user_pool_id = 'your-user-pool-id'
        self.app_client_id = 'your-app-client-id'
        
        self.users_table = self.dynamodb.Table('Users')
        self.products_table = self.dynamodb.Table('Products')
        self.cart_table = self.dynamodb.Table('Cart')

    async def is_online(self) -> bool:
        try:
            self.cognito.list_users(UserPoolId=self.user_pool_id, Limit=1)
            return True
        except ClientError:
            return False

    async def check_connection(self):
        """Verifica la conexión con AWS"""
        self.cognito.list_users(UserPoolId=self.user_pool_id, Limit=1)

    async def create_user(self, user: UserInDB):
        try:
            response = self.cognito.admin_create_user(
                UserPoolId=self.user_pool_id,
                Username=user.email,
                UserAttributes=[
                    {'Name': 'email', 'Value': user.email},
                    {'Name': 'name', 'Value': user.full_name},
                    {'Name': 'email_verified', 'Value': 'true'},
                ],
                TemporaryPassword="TempPass123!",  # En producción usar un método seguro
                MessageAction='SUPPRESS'
            )
            
            self.users_table.put_item(Item=user.dict())
            return response
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")

    async def verify_google_token(self, token: str) -> Optional[UserInDB]:
        try:
            # En producción usar la biblioteca oficial de Google
            return UserInDB(
                email="user@example.com",
                full_name="Google User",
                is_google_auth=True
            )
        except Exception:
            return None

    async def get_cart_items(self, user_id: str) -> List[CartItemInDB]:
        try:
            response = self.cart_table.query(
                KeyConditionExpression='userId = :userId',
                ExpressionAttributeValues={':userId': user_id}
            )
            return [CartItemInDB(**item) for item in response.get('Items', [])]
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")

    async def add_to_cart(self, cart_item: CartItemInDB):
        try:
            self.cart_table.put_item(Item=cart_item.dict())
            return cart_item
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")

    async def remove_from_cart(self, item_id: str):
        try:
            self.cart_table.delete_item(Key={'itemId': item_id})
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")

    async def update_cart_item(self, cart_item: CartItemInDB):
        try:
            self.cart_table.put_item(Item=cart_item.dict())
            return cart_item
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")

    async def get_all_products(self) -> List[Product]:
        try:
            response = self.products_table.scan()
            return [Product(**item) for item in response.get('Items', [])]
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")

    async def get_product_by_id(self, product_id: str) -> Product:
        try:
            response = self.products_table.get_item(Key={'id': product_id})
            return Product(**response['Item'])
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")

    async def create_product(self, product: Product):
        try:
            self.products_table.put_item(Item=product.dict())
            return product
        except ClientError as e:
            raise Exception(f"AWS Error: {e.response['Error']['Message']}")