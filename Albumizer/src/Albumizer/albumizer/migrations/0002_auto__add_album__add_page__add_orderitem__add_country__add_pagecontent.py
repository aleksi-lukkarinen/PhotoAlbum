# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Album'
        db.create_table('albumizer_album', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('isPublic', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.User'])),
        ))
        db.send_create_signal('albumizer', ['Album'])

        # Adding model 'Page'
        db.create_table('albumizer_page', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pageNumber', self.gf('django.db.models.fields.IntegerField')()),
            ('layoutID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Album'])),
        ))
        db.send_create_signal('albumizer', ['Page'])

        # Adding model 'OrderItem'
        db.create_table('albumizer_orderitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Order'])),
            ('album', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Album'])),
            ('deliveryAddress', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Address'])),
        ))
        db.send_create_signal('albumizer', ['OrderItem'])

        # Adding model 'Country'
        db.create_table('albumizer_country', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('albumizer', ['Country'])

        # Adding model 'PageContent'
        db.create_table('albumizer_pagecontent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('placeHolderID', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('page', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Page'])),
        ))
        db.send_create_signal('albumizer', ['PageContent'])

        # Adding model 'Order'
        db.create_table('albumizer_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('purchaseDate', self.gf('django.db.models.fields.DateTimeField')()),
            ('status', self.gf('django.db.models.fields.IntegerField')()),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.User'])),
        ))
        db.send_create_signal('albumizer', ['Order'])

        # Adding model 'Address'
        db.create_table('albumizer_address', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('streetAddress', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('postOffice', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('postCode', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('country', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['albumizer.Country'])),
        ))
        db.send_create_signal('albumizer', ['Address'])

        # Adding model 'User'
        db.create_table('albumizer_user', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('userName', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('facebookID', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('albumizer', ['User'])


    def backwards(self, orm):
        
        # Deleting model 'Album'
        db.delete_table('albumizer_album')

        # Deleting model 'Page'
        db.delete_table('albumizer_page')

        # Deleting model 'OrderItem'
        db.delete_table('albumizer_orderitem')

        # Deleting model 'Country'
        db.delete_table('albumizer_country')

        # Deleting model 'PageContent'
        db.delete_table('albumizer_pagecontent')

        # Deleting model 'Order'
        db.delete_table('albumizer_order')

        # Deleting model 'Address'
        db.delete_table('albumizer_address')

        # Deleting model 'User'
        db.delete_table('albumizer_user')


    models = {
        'albumizer.address': {
            'Meta': {'object_name': 'Address'},
            'country': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Country']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'postCode': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'postOffice': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'streetAddress': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'albumizer.album': {
            'Meta': {'object_name': 'Album'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'isPublic': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.User']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'albumizer.country': {
            'Meta': {'object_name': 'Country'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'albumizer.order': {
            'Meta': {'object_name': 'Order'},
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'purchaseDate': ('django.db.models.fields.DateTimeField', [], {}),
            'status': ('django.db.models.fields.IntegerField', [], {})
        },
        'albumizer.orderitem': {
            'Meta': {'object_name': 'OrderItem'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Album']"}),
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'deliveryAddress': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Address']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Order']"})
        },
        'albumizer.page': {
            'Meta': {'object_name': 'Page'},
            'album': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Album']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'layoutID': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'pageNumber': ('django.db.models.fields.IntegerField', [], {})
        },
        'albumizer.pagecontent': {
            'Meta': {'object_name': 'PageContent'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['albumizer.Page']"}),
            'placeHolderID': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'albumizer.user': {
            'Meta': {'object_name': 'User'},
            'facebookID': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'userName': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['albumizer']
