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


# 서비스 계층에 위임하는 Flask App
# 요청 전 상태를 관리하고, POST 파라미터로부터 정보를 파싱하며, 상태 코드를 응답하고, JSON을 처리한다.
@app.route("/allocate", methods=["POST"])
def allocate_endpoint():
    session = get_session()  # DB Session을 인스턴스화
    repo = repository.SqlAlchemyRepository(session)  # Repository 객체들도 인스턴스화
    line = model.OrderLine(  # 사용자의 명령들을 웹 request에서 추출
        request.json["orderid"],
        request.json["sku"],
        request.json["qty"],
    )

    try:
        batchref = model.allocate(line, repo, session)  # 추출한 명령을 Domain 서비스에 넘긴다.
    except model.OutOfStock as e:
        return jsonify({"message": str(e)}), 400  # 적절한 Status Code가 있는 JSON 응답을 반환한다.

    return {"batchref": batchref}, 201  # 적절한 Status Code가 있는 JSON 응답을 반환한다.
