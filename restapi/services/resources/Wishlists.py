from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.models.PropertyModel import Property
from services.models.UserModel import User
from services.schemas.properties.PropertySchema import PropertySchema

class LoveProperty(Resource):
    @jwt_required
    def post(self,property_id: int):
        property_db = Property.query.filter_by(id=property_id).first_or_404('Property not found')
        user = User.query.get(get_jwt_identity())
        if not User.check_wishlist(property_db.id,user.id):
            user.wishlists.append(property_db)
            user.save_to_db()
            return {"message":"Property entered into the wishlist"}, 200
        return {"message":"Property already in wishlist"}, 200

class UnloveProperty(Resource):
    @jwt_required
    def delete(self,property_id: int):
        property_db = Property.query.filter_by(id=property_id).first_or_404('Property not found')
        user = User.query.get(get_jwt_identity())
        if User.check_wishlist(property_db.id,user.id):
            user.delete_wishlist(property_db.id)
            return {"message":"Property remove from wishlist"}, 200
        return {"message":"Property not on wishlist"}, 200

class UserWishlist(Resource):
    @jwt_required
    def get(self):
        _property_schema = PropertySchema()
        per_page = request.args.get('per_page',default=6,type=int)
        page = request.args.get('page',default=1,type=int)

        type_id = request.args.get('type_id',default=None,type=int)
        status = request.args.get('status',default=None,type=str)
        period = request.args.get('period',default=None,type=str)

        args = {
            'type_id':type_id,
            'status':status,
            'period':period
        }

        user = User.query.get(get_jwt_identity())
        properties = user.get_wishlist_property(per_page=per_page,page=page,**args)

        data_property = [Property.query.get(x) for x in [j[1] for j in properties.items]]
        data = _property_schema.dump(data_property,many=True)

        results = dict(
            data = data,
            next_num = properties.next_num,
            prev_num = properties.prev_num,
            page = properties.page,
            iter_pages = [x for x in properties.iter_pages()]
        )

        return results, 200
