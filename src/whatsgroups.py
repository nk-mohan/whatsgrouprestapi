from flask import Blueprint, request
from flask.json import jsonify
import validators
from flask_jwt_extended import jwt_required
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_404_NOT_FOUND
from src.database import Group, db
from datetime import datetime
from flasgger import swag_from

whatsgroups = Blueprint("whatsgroups", __name__, url_prefix="/api/v1/whatsgroups")

@whatsgroups.post('/')
@jwt_required()
@swag_from("./docs/whatsgroups/create_group.yaml")
def groups():
    title = request.get_json().get("title", '')
    description = request.get_json().get("description", '')
    link = request.get_json().get("link", '')
    category = request.get_json().get("category", '')

    if len(link) == 0:
        return jsonify({
                "error":"Group Link should not be empty"
            }), HTTP_400_BAD_REQUEST

    if not validators.url(link):
        return jsonify({
                "error":"Group Link is not valid."
            }), HTTP_400_BAD_REQUEST

    if len(title) == 0:
        return jsonify({
                "error":"Group Name should not be empty"
            }), HTTP_400_BAD_REQUEST

    if len(description) == 0:
            return jsonify({
                "error":"Group Description should not be empty"
            }), HTTP_400_BAD_REQUEST

    if len(category) == 0:
            return jsonify({
                "error":"Category should be selected"
            }), HTTP_400_BAD_REQUEST

    if Group.query.filter_by(link=link).first():
            return jsonify({
                "error" : "Group Link already exists"
            }), HTTP_409_CONFLICT

    group = Group(title=title, description=description, link=link, category=category, created_at=datetime.now())
    db.session.add(group)
    db.session.commit()

    return jsonify({
            'id':group.id,
            'link':group.link,
            'created_at':group.created_at
        }), HTTP_201_CREATED


@whatsgroups.get('/')
@jwt_required()
@swag_from("./docs/whatsgroups/get_all_groups.yaml")
def get_all_groups():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    groups = Group.query.filter(Group.report_count < 100).order_by(Group.created_at.desc()).paginate(page=page, per_page=per_page)

    data = []

    for group in groups.items:
        data.append({
                "id": group.id,
                "title": group.title,
                "description": group.description,
                "link": group.link,
                "category": group.category,
                "views_count": group.views_count,
                "report_count": group.report_count,
                "created_at": group.created_at
            })

    meta = {
            "current_page": groups.page,
            "total_pages": groups.pages,
            "total_count": groups.total
        }

    return jsonify({"data": data, "meta": meta}), HTTP_200_OK

@whatsgroups.get("/<int:id>")
@jwt_required()
@swag_from("./docs/whatsgroups/get_single_group.yaml")
def get_group(id):
    group = Group.query.filter_by(id=id).first()

    if not group:
        return jsonify({"message": "Item not found"}), HTTP_404_NOT_FOUND
    else:
        return jsonify({
                "id": group.id,
                "title": group.title,
                "description": group.description,
                "link": group.link,
                "category": group.category,
                "views_count": group.views_count,
                "report_count": group.report_count,
                "created_at": group.created_at
            }), HTTP_200_OK

@whatsgroups.put("/<int:id>")
@jwt_required()
@swag_from("./docs/whatsgroups/update_views_of_the_group.yaml")
def update_views(id):
    group = Group.query.filter_by(id=id).first()

    if not group:
        return jsonify({"message": "Item not found"}), HTTP_404_NOT_FOUND
    
    group.views_count = group.views_count+1

    db.session.commit()

    return jsonify({"message": "Updated viewed status"}), HTTP_201_CREATED


@whatsgroups.put("/report/<int:id>")
@jwt_required()
@swag_from("./docs/whatsgroups/report_group.yaml")
def update_report(id):
    group = Group.query.filter_by(id=id).first()

    if not group:
        return jsonify({"message": "Item not found"}), HTTP_404_NOT_FOUND
    
    group.report_count = group.report_count+1

    db.session.commit()

    return jsonify({"message": "This group is reported"}), HTTP_201_CREATED

@whatsgroups.get("/trending/")
@jwt_required()
@swag_from("./docs/whatsgroups/get_trending_groups.yaml")
def get_trending_groups():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    groups = Group.query.filter(Group.report_count < 100).order_by(Group.views_count.desc(), Group.created_at.desc()).paginate(page=page, per_page=per_page)

    data = []

    for group in groups.items:
        data.append({
            "id": group.id,
            "title": group.title,
            "description": group.description,
            "link": group.link,
            "category": group.category,
            "views_count": group.views_count,
            "report_count": group.report_count,
            "created_at": group.created_at
        })

    meta = {
        "current_page": groups.page,
        "total_pages": groups.pages,
        "total_count": groups.total
    }

    return jsonify({"data": data, "meta": meta}), HTTP_200_OK


@whatsgroups.get("/category/<string:category_name>")
@jwt_required()
@swag_from("./docs/category/get_groups_by_category.yaml")
def get_groups_by_category(category_name):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    groups = Group.query.filter(Group.category == category_name, Group.report_count < 100).order_by(Group.created_at.desc()).paginate(page=page, per_page=per_page)

    data = []

    for group in groups.items:
        data.append({
            "id": group.id,
            "title": group.title,
            "description": group.description,
            "link": group.link,
            "category": group.category,
            "views_count": group.views_count,
            "report_count": group.report_count,
            "created_at": group.created_at
        })

    meta = {
        "current_page": groups.page,
        "total_pages": groups.pages,
        "total_count": groups.total
    }

    return jsonify({"data": data, "meta": meta}), HTTP_200_OK

@whatsgroups.get("/categories")
@jwt_required()
@swag_from("./docs/category/get_all_categories.yaml")
def get_categories():
    data = []
    data.append({"category_name": "Arts & Design", "category_link":"https://miro.medium.com/max/1100/1*7oDHINwJnMkuVXABXq-7Ag.webp"})
    data.append({"category_name": "Audios & Videos", "category_link":"https://miro.medium.com/max/1100/1*1pkPyPWu3-RpOc7w-nr48w.webp"})
    data.append({"category_name": "Business & Finance", "category_link":"https://miro.medium.com/max/1100/1*9NiwCghUdTo_l8bUg2mRag.webp"})
    data.append({"category_name": "Buy & Sell", "category_link":"https://miro.medium.com/max/1100/1*oBWVR7Df5DLBHvJX1xJ90Q.webp"})
    data.append({"category_name": "Community", "category_link":"https://miro.medium.com/max/828/1*s2EnWQKhsV7k-N3SxOYtKg.webp"})
    data.append({"category_name": "Education", "category_link":"https://miro.medium.com/max/1100/1*SXlmld_yZpEbj3UQFpcWxw.webp"})
    data.append({"category_name": "Entertainment", "category_link":"https://miro.medium.com/max/1100/1*19kqeD78XE0pl-htR2ki9w.webp"})
    data.append({"category_name": "Fitness & Health", "category_link":"https://miro.medium.com/max/828/1*oUlVUhSp-JvASrxzdtLltw.webp"})
    data.append({"category_name": "Food", "category_link":"https://miro.medium.com/max/828/1*MsTjZ9-CaQC9PLFmORKlIQ.webp"})
    data.append({"category_name": "Funny", "category_link":"https://miro.medium.com/max/828/1*OXxbjfwmUiqioKpausk_IQ.webp"})
    data.append({"category_name": "Games", "category_link":"https://miro.medium.com/max/828/1*bkQebiZ-EH4XJjX5zzz_5A.webp"})
    data.append({"category_name": "Love & Dating", "category_link":"https://miro.medium.com/max/1100/1*RXJsQ1y66ivB6S2M7JAg4Q.webp"})
    data.append({"category_name": "Medical", "category_link":"https://miro.medium.com/max/1100/1*JpcP2FQxirtnD35-vMmSsg.webp"})
    data.append({"category_name": "New Friends", "category_link":"https://miro.medium.com/max/1100/1*ARDmMTMn97P_5We379uBCQ.webp"})
    data.append({"category_name": "News", "category_link":"https://miro.medium.com/max/828/1*IYDC_q4coDrY6HHx0bglcQ.webp"})
    data.append({"category_name": "Social Media", "category_link":"https://miro.medium.com/max/828/1*lnV1BCzVyJSXFsApSScV2g.webp"})
    data.append({"category_name": "Spiritual", "category_link":"https://miro.medium.com/max/1100/1*b04NArpppdlS9x2698WFvg.webp"})
    data.append({"category_name": "Sports", "category_link":"https://miro.medium.com/max/1100/1*FMkUB_NDWASyyf5oPKXk3g.webp"})
    data.append({"category_name": "Technology", "category_link":"https://miro.medium.com/max/828/1*UYlesTZaj57WHDlRkdGMPA.webp"})
    data.append({"category_name": "Travels & Places", "category_link":"https://miro.medium.com/max/1100/1*GMTSCaECaXVLRwkbOUOXzw.webp"})
    data.append({"category_name": "Other", "category_link":"https://miro.medium.com/max/1100/1*9aS447bTO9-S-cUjkUyeMw.webp"})

    return jsonify({"categories":data}), HTTP_200_OK

