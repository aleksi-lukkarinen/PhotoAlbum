# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'UserProfile'
        db.create_table('albumizer_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('serviceConditionsAccepted', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('homePhone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal('albumizer', ['UserProfile'])

        # Adding model 'FacebookProfile'
        db.create_table('albumizer_facebookprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userProfile', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['albumizer.UserProfile'], unique=True)),
            ('facebookID', self.gf('django.db.models.fields.BigIntegerField')(unique=True)),
            ('token', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('profileUrl', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
        ))
        db.send_create_signal('albumizer', ['FacebookProfile'])

        # Adding model 'Album'
        db.create_table('albumizer_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('isPublic', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('albumizer', ['Album'])

        # Adding unique constraint on 'Album', fields ['owner', 'title']
        db.create_unique('albumizer_album', ['owner_id', 'title'])

        # Adding model 'Page'
        db.create_table('albumizer_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Album'])),
            ('pageNumber', self.gf('django.db.models.fields.IntegerField')()),
            ('layoutID', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('albumizer', ['Page'])

        # Adding unique constraint on 'Page', fields ['album', 'pageNumber']
        db.create_unique('albumizer_page', ['album_id', 'pageNumber'])

        # Adding model 'PageContent'
        db.create_table('albumizer_pagecontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Page'])),
            ('placeHolderID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('albumizer', ['PageContent'])

        # Adding unique constraint on 'PageContent', fields ['page', 'placeHolderID']
        db.create_unique('albumizer_pagecontent', ['page_id', 'placeHolderID'])

        # Adding model 'Country'
        db.create_table('albumizer_country', (
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('albumizer', ['Country'])

        # Adding model 'State'
        db.create_table('albumizer_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('albumizer', ['State'])

        # Adding model 'Address'
        db.create_table('albumizer_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('postAddressLine1', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('postAddressLine2', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('zipCode', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.State'], null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Country'], null=True, blank=True)),
        ))
        db.send_create_signal('albumizer', ['Address'])

        # Adding model 'Order'
        db.create_table('albumizer_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('orderer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('purchaseDate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('albumizer', ['Order'])

        # Adding unique constraint on 'Order', fields ['orderer', 'purchaseDate']
        db.create_unique('albumizer_order', ['orderer_id', 'purchaseDate'])

        # Adding model 'OrderItem'
        db.create_table('albumizer_orderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Order'])),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Album'])),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('deliveryAddress', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Address'])),
        ))
        db.send_create_signal('albumizer', ['OrderItem'])

        # Adding unique constraint on 'OrderItem', fields ['order', 'album']
        db.create_unique('albumizer_orderitem', ['order_id', 'album_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'OrderItem', fields ['order', 'album']
        db.delete_unique('albumizer_orderitem', ['order_id', 'album_id'])

        # Removing unique constraint on 'Order', fields ['orderer', 'purchaseDate']
        db.delete_unique('albumizer_order', ['orderer_id', 'purchaseDate'])

        # Removing unique constraint on 'PageContent', fields ['page', 'placeHolderID']
        db.delete_unique('albumizer_pagecontent', ['page_id', 'placeHolderID'])

        # Removing unique constraint on 'Page', fields ['album', 'pageNumber']
        db.delete_unique('albumizer_page', ['album_id', 'pageNumber'])

        # Removing unique constraint on 'Album', fields ['owner', 'title']
        db.delete_unique('albumizer_album', ['owner_id', 'title'])

        # Deleting model 'UserProfile'
        db.delete_table('albumizer_userprofile')

        # Deleting model 'FacebookProfile'
        db.delete_table('albumizer_facebookprofile')

        # Deleting model 'Album'
        db.delete_table('albumizer_album')

        # Deleting model 'Page'
        db.delete_table('albumizer_page')

        # Deleting model 'PageContent'
        db.delete_table('albumizer_pagecontent')

        # Deleting model 'Country'
        db.delete_table('albumizer_country')

        # Deleting model 'State'
        db.delete_table('albumizer_state')

        # Deleting model 'Address'
        db.delete_table('albumizer_address')

        # Deleting model 'Order'
        db.delete_table('albumizer_order')

        # Deleting model 'OrderItem'
        db.delete_table('albumizer_orderitem')


    models = {
        'albumizer.address': {
            'Meta': {'ordering': "['owner', 'postAddressLine1']", 'object_name': 'Address'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Country']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'postAddressLine1': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'postAddressLine2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'state': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.State']", 'null': 'True', 'blank': 'True'}),
            'zipCode': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'albumizer.album': {
            'Meta': {'ordering': "['owner', 'title']", 'unique_together': "(('owner', 'title'),)", 'object_name': 'Album'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isPublic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'albumizer.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'albumizer.facebookprofile': {
            'Meta': {'object_name': 'FacebookProfile'},
            'facebookID': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'profileUrl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'userProfile': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['albumizer.UserProfile']", 'unique': 'True'})
        },
        'albumizer.order': {
            'Meta': {'ordering': "['orderer', 'purchaseDate', 'status']", 'unique_together': "(('orderer', 'purchaseDate'),)", 'object_name': 'Order'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orderer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'purchaseDate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        'albumizer.orderitem': {
            'Meta': {'ordering': "['order', 'album']", 'unique_together': "(('order', 'album'),)", 'object_name': 'OrderItem'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Album']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'deliveryAddress': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Address']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Order']"})
        },
        'albumizer.page': {
            'Meta': {'ordering': "['album', 'pageNumber']", 'unique_together': "(('album', 'pageNumber'),)", 'object_name': 'Page'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Album']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layoutID': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pageNumber': ('django.db.models.fields.IntegerField', [], {})
        },
        'albumizer.pagecontent': {
            'Meta': {'unique_together': "(('page', 'placeHolderID'),)", 'object_name': 'PageContent'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Page']"}),
            'placeHolderID': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'albumizer.state': {
            'Meta': {'ordering': "['name']", 'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'albumizer.userprofile': {
            'Meta': {'ordering': "['user']", 'object_name': 'UserProfile'},
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'homePhone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'serviceConditionsAccepted': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['albumizer']
