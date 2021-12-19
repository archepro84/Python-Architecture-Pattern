# Flask와 Postgres DB와 통신하기 위한 Python Script

from flask import Flask, jsonify, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import config
import model
import orm
import repository

orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_uri()))
app = Flask(__name__)


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


# E2E Test 개수가 제어가 가능한 수준을 넘었고, 역 피라미드형 테스트가 된다.
@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()
    batches = repository.SqlAlchemyRepository(session).list()
    line = model.OrderLine(
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    if not is_valid_sku(line.sku, batches):
        return jsonify({"message": f"Invalid sku {line.sku}"}), 400

    try:
        batchref = model.allocate(line, batches)
    except model.OutOfStock as e:
        return jsonify({"message": str(e)}), 400

    session.commit()  # 최종 DB Commit
    return {"batchref": batchref}, 201
