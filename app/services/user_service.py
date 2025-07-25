from app import db
from app.models.recycle_log import RecycleLog
from app.models.user import User
from sqlalchemy import func


# 홈화면
def get_user_home_info(user_id):
    # 사용자 정보 조회
    user = User.query.get(user_id)

    if not user:
        return {"msg": "사용자를 찾을 수 없습니다."}, 404

    # 품목별 재활용 횟수 조회 (is_successful=True 조건 추가)
    recycle_counts = db.session.query(
        RecycleLog.trash_type,
        func.sum(RecycleLog.recycle_count).label('total_recycles')
    ).filter_by(user_id=user_id, is_successful=True).group_by(RecycleLog.trash_type).all()

    recycle_count_dict = {item.trash_type: item.total_recycles for item in recycle_counts}

    # 최근 재활용 내역 3개 조회 (시간, 품목, 얻은 포인트) - is_successful=True 조건 추가
    recent_recycles = RecycleLog.query.filter_by(user_id=user_id, is_successful=True).order_by(RecycleLog.timestamp.desc()).limit(3).all()

    # 사용자 정보, 포인트, 품목별 재활용 횟수, 최근 재활용 내역 반환
    return {
        "nickname": user.nickname,
        "total_points": user.points,  # 사용자 포인트
        "recycle_counts": recycle_count_dict,
        "recent_recycles": [
            {
                "trash_type": log.trash_type,
                "earned_points": log.earned_points,  # 얻은 포인트
                "timestamp": log.timestamp_kst.strftime('%Y-%m-%d %H:%M:%S')  # KST로 변환된 재활용 시간
            }
            for log in recent_recycles
        ]
    }, 200


# 재활용 내역
def get_user_recycle_logs(user_id):
    # 사용자 정보 조회
    user = User.query.get(user_id)

    if not user:
        return {"msg": "사용자를 찾을 수 없습니다."}, 404

    # 품목별 재활용 횟수 조회 (is_successful=True 조건 추가)
    recycle_counts = db.session.query(
        RecycleLog.trash_type,
        func.sum(RecycleLog.recycle_count).label('total_recycles')
    ).filter_by(user_id=user_id, is_successful=True).group_by(RecycleLog.trash_type).all()

    recycle_count_dict = {item.trash_type: item.total_recycles for item in recycle_counts}

    # 전체 재활용 내역 조회 (is_successful=True 조건 추가)
    recent_recycles = RecycleLog.query.filter_by(user_id=user_id, is_successful=True).order_by(RecycleLog.timestamp.desc()).all()

    # 사용자 정보, 포인트, 품목별 재활용 횟수, 전체 재활용 내역 반환
    return {
        "recycle_counts": recycle_count_dict,
        "recent_recycles": [
            {
                "trash_type": log.trash_type,
                "earned_points": log.earned_points,  # 얻은 포인트
                "timestamp": log.timestamp_kst.strftime('%Y-%m-%d %H:%M:%S')  # KST로 변환된 재활용 시간
            }
            for log in recent_recycles
        ]
    }, 200


# 포인트 내역
def get_user_points_logs(user_id):

    # 사용자 정보 조회
    user = User.query.get(user_id)

    if not user:
        return {"msg": "사용자를 찾을 수 없습니다."}, 404

    # 포인트 변동이 있는 로그만 조회 (earned_points가 0이 아닌 경우)
    recycle_logs = RecycleLog.query.filter(
        RecycleLog.user_id == user_id,
        RecycleLog.earned_points != 0  # 포인트 변동이 있는 경우만 포함
    ).order_by(RecycleLog.timestamp.desc()).all()

    # 포인트 변동 내역을 한 줄에 하나씩 추가
    point_log_list = [
        {
            "timestamp": log.timestamp_kst.strftime('%Y-%m-%d %H:%M:%S'),  # KST로 변환된 시간
            "points_change": log.earned_points  # 얻은 포인트 (양수: 획득, 음수: 사용)
        }
        for log in recycle_logs
    ]

    # 전체 포인트와 포인트 변동 내역 반환
    return {
        "total_points": user.points,  # 사용자 전체 포인트
        "points_logs": point_log_list  # 포인트 변동 내역 리스트 (변동이 있는 경우만)
    }, 200
