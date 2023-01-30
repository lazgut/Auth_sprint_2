from flask import Request
from models.history import HistoryModel
from sqlalchemy.dialects.postgresql import UUID


class HistoryService:
    def __init__(self, db):
        self.db = db

    def store_history(self, user_id: UUID, request: Request) -> bool:
        device = request.headers.get(
            'sec-ch-ua-platform', request.headers.get('User_Agent')
        )
        record = self._create_record(user_id, device)
        self.db.session.add(record)
        self.db.session.commit()

    def _create_record(self, user_id: UUID, device: str) -> HistoryModel:
        access_record = HistoryModel(
            user_id=user_id,
            device=device,
        )
        return access_record

    def get_history(self, user_id: UUID, page=1) -> list[HistoryModel]:
        pagination = HistoryModel.query.filter_by(user_id=user_id).paginate(
            page=page, per_page=10
        )
        return list(pagination.items)
