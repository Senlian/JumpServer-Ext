# Generated by Django 2.2.10 on 2020-08-13 12:05

import common.fields.model
import common.utils.django
import django.contrib.auth.models
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.utils.timezone
import users.models.user
import uuid

# 添加Default组
def add_default_group(apps, schema_editor):
    group_model = apps.get_model("users", "UserGroup")
    db_alias = schema_editor.connection.alias
    group_model.objects.using(db_alias).create(
        name="Default"
    )

# 添加默认用户
def add_default_admin(apps, schema_editor):
    user_model = apps.get_model("users", "User")
    db_alias = schema_editor.connection.alias
    admin = user_model.objects.using(db_alias).create(
        username="admin", name="Administrator",
        email="admin@mycomany.com", role="Admin",
        password=make_password("admin"),
    )
    group_model = apps.get_model("users", "UserGroup")
    default_group = group_model.objects.using(db_alias).get(name="Default")
    admin.groups.add(default_group)

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('org_id', models.CharField(blank=True, db_index=True, default='', max_length=36, verbose_name='Organization')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date created')),
                ('created_by', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'verbose_name': 'User group',
                'ordering': ['name'],
                'unique_together': {('org_id', 'name')},
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=128, unique=True, verbose_name='Username')),
                ('name', models.CharField(max_length=128, verbose_name='Name')),
                ('email', models.EmailField(max_length=128, unique=True, verbose_name='Email')),
                ('role', models.CharField(blank=True, choices=[('Admin', 'Administrator'), ('User', 'User'), ('App', 'Application'), ('Auditor', 'Auditor'), ('CIE', 'CIE')], default='User', max_length=10, verbose_name='Role')),
                ('avatar', models.ImageField(null=True, upload_to='avatar', verbose_name='Avatar')),
                ('wechat', models.CharField(blank=True, max_length=128, verbose_name='Wechat')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone')),
                ('mfa_level', models.SmallIntegerField(choices=[(0, 'Disable'), (1, 'Enable'), (2, 'Force enable')], default=0, verbose_name='MFA')),
                ('otp_secret_key', common.fields.model.EncryptCharField(blank=True, max_length=128, null=True)),
                ('private_key', common.fields.model.EncryptTextField(blank=True, null=True, verbose_name='Private key')),
                ('public_key', common.fields.model.EncryptTextField(blank=True, null=True, verbose_name='Public key')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('is_first_login', models.BooleanField(default=True)),
                ('date_expired', models.DateTimeField(blank=True, db_index=True, default=common.utils.django.date_expired_default, null=True, verbose_name='Date expired')),
                ('created_by', models.CharField(blank=True, default='', max_length=30, verbose_name='Created by')),
                ('source', models.CharField(choices=[('local', 'Local'), ('ldap', 'LDAP/AD'), ('openid', 'OpenID'), ('radius', 'Radius'), ('cas', 'CAS')], default='local', max_length=30, verbose_name='Source')),
                ('date_password_last_updated', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Date password last updated')),
                ('groups', models.ManyToManyField(blank=True, related_name='users', to='users.UserGroup', verbose_name='User group')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'ordering': ['username'],
            },
            bases=(users.models.user.AuthMixin, users.models.user.TokenMixin, users.models.user.RoleMixin, users.models.user.MFAMixin, models.Model),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RunPython(add_default_group),
        migrations.RunPython(add_default_admin),
    ]
