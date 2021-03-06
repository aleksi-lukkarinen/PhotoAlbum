# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'PageContent.image'
        db.add_column('albumizer_pagecontent', 'image', self.gf('django.db.models.fields.files.ImageField')(default='', max_length=100, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'PageContent.image'
        db.delete_column('albumizer_pagecontent', 'image')


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
            'creationDate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isPublic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'secretHash': ('django.db.models.fields.TextField', [], {'max_length': '64'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'albumizer.country': {
            'Meta': {'ordering': "['name']", 'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'})
        },
        'albumizer.facebookprofile': {
            'Meta': {'ordering': "['userProfile']", 'object_name': 'FacebookProfile'},
            'facebookID': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lastQueryTime': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'profileUrl': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'rawResponse': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'token': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'userProfile': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'facebookProfile'", 'unique': 'True', 'to': "orm['albumizer.UserProfile']"})
        },
        'albumizer.layout': {
            'Meta': {'ordering': "['name']", 'object_name': 'Layout'},
            'cssClass': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'cssContent': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imageFieldCount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'textFieldCount': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'albumizer.order': {
            'Meta': {'ordering': "['orderer', 'purchaseDate', 'status']", 'unique_together': "(('orderer', 'purchaseDate'),)", 'object_name': 'Order'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'orderer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'purchaseDate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.OrderStatus']"}),
            'statusClarification': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'albumizer.orderitem': {
            'Meta': {'ordering': "['order', 'album']", 'unique_together': "(('order', 'album'),)", 'object_name': 'OrderItem'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Album']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'deliveryAddress': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Address']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Order']"})
        },
        'albumizer.orderstatus': {
            'Meta': {'ordering': "['id']", 'object_name': 'OrderStatus'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'albumizer.page': {
            'Meta': {'ordering': "['album', 'pageNumber']", 'unique_together': "(('album', 'pageNumber'),)", 'object_name': 'Page'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Album']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Layout']"}),
            'pageNumber': ('django.db.models.fields.IntegerField', [], {})
        },
        'albumizer.pagecontent': {
            'Meta': {'unique_together': "(('page', 'placeHolderID'),)", 'object_name': 'PageContent'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pagecontents'", 'to': "orm['albumizer.Page']"}),
            'placeHolderID': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'albumizer.shoppingcartitem': {
            'Meta': {'ordering': "['user', 'album']", 'unique_together': "(('additionDate', 'user', 'album'),)", 'object_name': 'ShoppingCartItem'},
            'additionDate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Album']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'deliveryAddress': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Address']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'albumizer.spspayment': {
            'Meta': {'ordering': "['order']", 'object_name': 'SPSPayment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2'}),
            'clarification': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['albumizer.Order']", 'unique': 'True'}),
            'referenceCode': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transactionDate': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
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
