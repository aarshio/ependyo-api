from flask import request, jsonify, Blueprint 
from server import db
from server.models import User, Post, Item
import jwt
import uuid

items = Blueprint('items', __name__)

@items.route('/api/all_items', methods=['GET', 'POST'])
def all_items():
    if request.method == 'GET':
        items = [z.to_json() for z in Item.query]
        return jsonify({'items':list(items)})
    return jsonify({'item':'invalid'})


@items.route('/api/get_item', methods=['GET', 'POST'])
def get_item():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'id': init_data.get('id')}
         item = Item.query.get(data['id'])
         return jsonify({'item':item.to_json()})

@items.route('/api/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'name': init_data.get('name'), 
                'category': init_data.get('category'),
                'price': init_data.get('price'), 
                'size': init_data.get('size'),
                'res1': init_data.get('res1'),
                'res2': init_data.get('res2'),
                'cpu': init_data.get('cpu'),
                'memory': init_data.get('memory'),
                'storage': init_data.get('storage'),
                'battery': init_data.get('battery')}
                
         item_1 = Item(id=uuid.uuid4().hex,name=data["name"], category=data["category"], details={'Price': data["price"], 'Screen Size': data["size"] , 'Resolution':[data["res1"] , data["res2"]], 'CPU':data["cpu"], 'Memory':data["memory"], 'Max Storage': data["storage"], 'Battery': data['battery']}, rating={'design': -1, 'durability': -1, 'camera': -1, 'features': -1, 'battery': -1, 'performance': -1, 'overall': -1 })
         db.session.add(item_1)
         db.session.commit()
        
@items.route('/api/remove_item', methods=['GET', 'POST'])
def remove_item():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = { 'id' : init_data.get('id')}
         Item.query.filter_by(id=data['id']).delete()
         db.session.commit()
         return jsonify({'status':"deleted"})

@items.route('/api/get_overall', methods=['GET', 'POST'])
def get_overall():
    if request.method == 'GET':
         items = [z.to_json() for z in Item.query]
         li = sorted(items, key=lambda x: x['rating']['overall'], reverse=True)
         return jsonify({'top':li[0:5]})

@items.route('/api/get_best', methods=['GET', 'POST'])
def get_best():
    if request.method == 'GET':
         items = [z.to_json() for z in Item.query]
         battery = max(items, key=lambda x: x['rating']['battery'])
         camera = max(items, key=lambda x: x['rating']['camera'])
         design = max(items, key=lambda x: x['rating']['design'])
         durability = max(items, key=lambda x: x['rating']['durability'])
         features = max(items, key=lambda x: x['rating']['features'])
         performance = max(items, key=lambda x: x['rating']['performance'])
         return jsonify({'battery':battery, 'camera':camera, 'design':design, 'durability':durability,
         'features': features, 'performance':performance})