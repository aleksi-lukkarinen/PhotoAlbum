# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Album', fields ['title']
        db.delete_unique('albumizer_album', ['title'])

        # Deleting model 'User'
        db.delete_table('albumizer_user')

        # Adding model 'UserProfile'
        db.create_table('albumizer_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('serviceConditionsAccepted', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('homePhone', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('facebookID', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('albumizer', ['UserProfile'])

        # Adding model 'State'
        db.create_table('albumizer_state', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal('albumizer', ['State'])

        # Changing field 'Album.owner'
        db.alter_column('albumizer_album', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Adding unique constraint on 'Album', fields ['owner', 'title']
        db.create_unique('albumizer_album', ['owner_id', 'title'])

        # Adding unique constraint on 'Page', fields ['album', 'pageNumber']
        db.create_unique('albumizer_page', ['album_id', 'pageNumber'])

        # Adding unique constraint on 'OrderItem', fields ['album', 'order']
        db.create_unique('albumizer_orderitem', ['album_id', 'order_id'])

        # Deleting field 'Country.id'
        db.delete_column('albumizer_country', 'id')

        # Changing field 'Country.code'
        db.alter_column('albumizer_country', 'code', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True))

        # Adding unique constraint on 'Country', fields ['code']
        db.create_unique('albumizer_country', ['code'])

        # Changing field 'Country.name'
        db.alter_column('albumizer_country', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100))

        # Adding unique constraint on 'Country', fields ['name']
        db.create_unique('albumizer_country', ['name'])

        # Deleting field 'Address.streetAddress'
        db.delete_column('albumizer_address', 'streetAddress')

        # Deleting field 'Address.postOffice'
        db.delete_column('albumizer_address', 'postOffice')

        # Deleting field 'Address.postCode'
        db.delete_column('albumizer_address', 'postCode')

        # Adding field 'Address.owner'
        db.add_column('albumizer_address', 'owner', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['auth.User']), keep_default=False)

        # Adding field 'Address.postAddressLine1'
        db.add_column('albumizer_address', 'postAddressLine1', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True), keep_default=False)

        # Adding field 'Address.postAddressLine2'
        db.add_column('albumizer_address', 'postAddressLine2', self.gf('django.db.models.fields.CharField')(default='', max_length=100, blank=True), keep_default=False)

        # Adding field 'Address.zipCode'
        db.add_column('albumizer_address', 'zipCode', self.gf('django.db.models.fields.CharField')(default='', max_length=10, blank=True), keep_default=False)

        # Adding field 'Address.city'
        db.add_column('albumizer_address', 'city', self.gf('django.db.models.fields.CharField')(default='', max_length=50, blank=True), keep_default=False)

        # Adding field 'Address.state'
        db.add_column('albumizer_address', 'state', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.State'], null=True, blank=True), keep_default=False)

        # Changing field 'Address.country'
        db.alter_column('albumizer_address', 'country_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Country'], null=True))

        # Deleting field 'Order.customer'
        db.delete_column('albumizer_order', 'customer_id')

        # Adding field 'Order.orderer'
        db.add_column('albumizer_order', 'orderer', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['auth.User']), keep_default=False)

        # Changing field 'Order.purchaseDate'
        db.alter_column('albumizer_order', 'purchaseDate', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True))

        # Adding unique constraint on 'Order', fields ['purchaseDate', 'orderer']
        db.create_unique('albumizer_order', ['purchaseDate', 'orderer_id'])

        # Adding unique constraint on 'PageContent', fields ['page', 'placeHolderID']
        db.create_unique('albumizer_pagecontent', ['page_id', 'placeHolderID'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PageContent', fields ['page', 'placeHolderID']
        db.delete_unique('albumizer_pagecontent', ['page_id', 'placeHolderID'])

        # Removing unique constraint on 'Order', fields ['purchaseDate', 'orderer']
        db.delete_unique('albumizer_order', ['purchaseDate', 'orderer_id'])

        # Removing unique constraint on 'Country', fields ['name']
        db.delete_unique('albumizer_country', ['name'])

        # Removing unique constraint on 'Country', fields ['code']
        db.delete_unique('albumizer_country', ['code'])

        # Removing unique constraint on 'OrderItem', fields ['album', 'order']
        db.delete_unique('albumizer_orderitem', ['album_id', 'order_id'])

        # Removing unique constraint on 'Page', fields ['album', 'pageNumber']
        db.delete_unique('albumizer_page', ['album_id', 'pageNumber'])

        # Removing unique constraint on 'Album', fields ['owner', 'title']
        db.delete_unique('albumizer_album', ['owner_id', 'title'])

        # Adding model 'User'
        db.create_table('albumizer_user', (
            ('userName', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('facebookID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('albumizer', ['User'])

        # Deleting model 'UserProfile'
        db.delete_table('albumizer_userprofile')

        # Deleting model 'State'
        db.delete_table('albumizer_state')

        # Changing field 'Album.owner'
        db.alter_column('albumizer_album', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.User']))

        # Adding unique constraint on 'Album', fields ['title']
        db.create_unique('albumizer_album', ['title'])

        # User chose to not deal with backwards NULL issues for 'Country.id'
        raise RuntimeError("Cannot reverse this migration. 'Country.id' and its values cannot be restored.")

        # Changing field 'Country.code'
        db.alter_column('albumizer_country', 'code', self.gf('django.db.models.fields.CharField')(max_length=10))

        # Changing field 'Country.name'
        db.alter_column('albumizer_country', 'name', self.gf('django.db.models.fields.CharField')(max_length=255))

        # User chose to not deal with backwards NULL issues for 'Address.streetAddress'
        raise RuntimeError("Cannot reverse this migration. 'Address.streetAddress' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Address.postOffice'
        raise RuntimeError("Cannot reverse this migration. 'Address.postOffice' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Address.postCode'
        raise RuntimeError("Cannot reverse this migration. 'Address.postCode' and its values cannot be restored.")

        # Deleting field 'Address.owner'
        db.delete_column('albumizer_address', 'owner_id')

        # Deleting field 'Address.postAddressLine1'
        db.delete_column('albumizer_address', 'postAddressLine1')

        # Deleting field 'Address.postAddressLine2'
        db.delete_column('albumizer_address', 'postAddressLine2')

        # Deleting field 'Address.zipCode'
        db.delete_column('albumizer_address', 'zipCode')

        # Deleting field 'Address.city'
        db.delete_column('albumizer_address', 'city')

        # Deleting field 'Address.state'
        db.delete_column('albumizer_address', 'state_id')

        # User chose to not deal with backwards NULL issues for 'Address.country'
        raise RuntimeError("Cannot reverse this migration. 'Address.country' and its values cannot be restored.")

        # User chose to not deal with backwards NULL issues for 'Order.customer'
        raise RuntimeError("Cannot reverse this migration. 'Order.customer' and its values cannot be restored.")

        # Deleting field 'Order.orderer'
        db.delete_column('albumizer_order', 'orderer_id')

        # Changing field 'Order.purchaseDate'
        db.alter_column('albumizer_order', 'purchaseDate', self.gf('django.db.models.fields.DateTimeField')())


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
            'facebookID': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
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
