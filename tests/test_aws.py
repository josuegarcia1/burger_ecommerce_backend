import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
from dotenv import load_dotenv
from decimal import Decimal
import time

load_dotenv()

class AWSTester:
    def __init__(self):
        # Obtener y limpiar la región
        self.region = os.getenv("AWS_REGION")
        self.session = boto3.Session(
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=self.region
        )
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        self.app_client_id = os.getenv("COGNITO_APP_CLIENT_ID")
        
    def print_header(self, message):
        print(f"\n{'='*50}")
        print(f"🧪 {message}")
        print('='*50)
        
    def test_credentials(self):
        self.print_header("1. Probando Credenciales AWS")
        try:
            sts = self.session.client('sts')
            identity = sts.get_caller_identity()
            print(f"✅ Usuario IAM válido: {identity['Arn']}")
            return True
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
    
    def test_dynamodb_tables(self):
        self.print_header("2. Probando Tablas DynamoDB")
        try:
            dynamodb = self.session.resource('dynamodb')
            required_tables = {"Users", "Products", "Cart"}
            existing_tables = set()
            
            for table_name in required_tables:
                try:
                    table = dynamodb.Table(table_name)
                    table.load()  # Verifica que la tabla exista
                    existing_tables.add(table_name)
                    print(f"✅ Tabla '{table_name}' existe")
                except ClientError as e:
                    if e.response['Error']['Code'] == 'ResourceNotFoundException':
                        print(f"❌ Tabla faltante: '{table_name}'")
                    else:
                        raise
            
            if required_tables - existing_tables:
                return False
            return True
            
        except Exception as e:
            print(f"❌ Error inesperado: {str(e)}")
            return False
    
    def test_dynamodb_crud(self):
        self.print_header("3. Probando Operaciones DynamoDB (CRUD)")
        try:
            dynamodb = self.session.resource('dynamodb')
            table = dynamodb.Table('Products')
            test_id = f"test_{int(time.time())}"
            
            # Create
            item = {
                'id': test_id,
                'name': 'Hamburguesa Test',
                'price': Decimal('9.99'),
                'category': 'test'
            }
            table.put_item(Item=item)
            print("✅ Create: Item insertado")
            
            # Read
            response = table.get_item(Key={'id': test_id})
            if 'Item' not in response:
                print("❌ Read: No se encontró el item")
                return False
            print(f"✅ Read: Item obtenido - {response['Item']}")
            
            # Delete
            table.delete_item(Key={'id': test_id})
            print("✅ Delete: Item eliminado")
            return True
            
        except Exception as e:
            print(f"❌ Error en CRUD: {str(e)}")
            return False
    
    def test_cognito(self):
        self.print_header("4. Probando Cognito User Pool")
        try:
            cognito = self.session.client('cognito-idp')
            
            # Verificar User Pool
            pool = cognito.describe_user_pool(UserPoolId=self.user_pool_id)
            print(f"✅ User Pool: {pool['UserPool']['Name']}")
            
            # Verificar App Client
            client = cognito.describe_user_pool_client(
                UserPoolId=self.user_pool_id,
                ClientId=self.app_client_id
            )
            print(f"✅ App Client: {client['UserPoolClient']['ClientName']}")
            return True
            
        except Exception as e:
            print(f"❌ Error en Cognito: {str(e)}")
            return False
    
    def test_cognito_signup(self):
        self.print_header("5. Probando Registro de Usuario")
        test_username = None
        try:
            cognito = self.session.client('cognito-idp')
            test_username = f"testuser_{int(time.time())}"  # Username sin formato email
            test_email = f"{test_username}@example.com"
            
            # 1. Registro con username sin formato email
            response = cognito.sign_up(
                ClientId=self.app_client_id,
                Username=test_username,  # Cambiado de test_email a test_username
                Password="TestPass123!$",  # Asegúrate que cumple las políticas
                UserAttributes=[
                    {'Name': 'email', 'Value': test_email},
                    {'Name': 'preferred_username', 'Value': test_username},
                    {'Name': 'given_name', 'Value': 'Test'},
                    {'Name': 'family_name', 'Value': 'User'}
                ]
            )
            print(f"✅ Usuario registrado: {response['UserSub']}")

            # 2. Confirmación (si el pool requiere verificación)
            try:
                cognito.admin_confirm_sign_up(
                    UserPoolId=self.user_pool_id,
                    Username=test_username
                )
                print("✅ Usuario confirmado")
            except Exception as confirm_error:
                print(f"⚠️ Usuario registrado pero no confirmado: {str(confirm_error)}")

            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'UsernameExistsException':
                print("❌ Error: El usuario ya existe")
            elif error_code == 'InvalidPasswordException':
                print("❌ Error: La contraseña no cumple los requisitos")
            else:
                print(f"❌ Error ({error_code}): {e.response['Error']['Message']}")
            return False
            
        finally:
            # Limpieza garantizada
            if test_username:
                try:
                    cognito.admin_delete_user(
                        UserPoolId=self.user_pool_id,
                        Username=test_username
                    )
                    print("✅ Usuario de prueba eliminado")
                except Exception as delete_error:
                    print(f"⚠️ Error limpiando usuario: {str(delete_error)}")

def main():
    tester = AWSTester()
    
    tests = [
        ("Credenciales", tester.test_credentials),
        ("Tablas DynamoDB", tester.test_dynamodb_tables),
        ("Operaciones DynamoDB", tester.test_dynamodb_crud),
        ("Configuración Cognito", tester.test_cognito),
        ("Registro de Usuario", tester.test_cognito_signup)
    ]
    
    all_passed = True
    for name, test in tests:
        if not test():
            print(f"\n⚠️ La prueba '{name}' falló")
            all_passed = False
            break
    
    if all_passed:
        print("\n🎉 ¡Todas las pruebas pasaron correctamente!")
    else:
        print("\n🔴 Algunas pruebas fallaron. Revisa los mensajes de error.")

if __name__ == "__main__":
    main()