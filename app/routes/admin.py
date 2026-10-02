from datetime import datetime, timedelta
import logging
import uuid

from flask import Blueprint, abort, jsonify, redirect, render_template, request, session, url_for

from app.routes.auth import get_supabase_client, get_supabase_service_client


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


MOCK_PRODUCTS = [
    {
        "id": "mock-1", "name": "14K 골드 도금 볼드 드롭 귀걸이", "code": "VF-AC-006",
        "category": "주얼리", "price": 32000, "discount_price": 29000,
        "options": "골드", "stock": 18, "safe_stock": 5, "status": "판매중",
        "registered_at": "2026-09-28", "image": "https://images.unsplash.com/photo-1630019852942-f89202989a59?w=160&auto=format&fit=crop&q=80",
        "description": "은은한 골드 광택과 감각적인 곡선이 돋보이는 모던 드롭 이어링입니다.",
    },
    {
        "id": "mock-2", "name": "1부 다이아 데끌라 프로포즈 목걸이", "code": "VF-JW-001",
        "category": "주얼리", "price": 395000, "discount_price": 356000,
        "options": "화이트골드, 로즈골드", "stock": 4, "safe_stock": 5, "status": "판매중",
        "registered_at": "2026-09-25", "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=160&auto=format&fit=crop&q=80",
        "description": "물방울 라인 프레임에 세팅된 영롱한 1부 다이아몬드 프로포즈 목걸이입니다.",
    },
    {
        "id": "mock-3", "name": "KUMTTON 스퀘어 자개 다이얼 실버 메쉬 시계", "code": "VF-WT-005",
        "category": "시계", "price": 128000, "discount_price": 89000,
        "options": "실버 / FREE", "stock": 12, "safe_stock": 4, "status": "판매중",
        "registered_at": "2026-09-21", "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=160&auto=format&fit=crop&q=80",
        "description": "우아한 스퀘어 실버 프레임과 은은한 자개 다이얼의 쿼츠 시계입니다.",
    },
    {
        "id": "mock-4", "name": "베이직 헤비 코튼 크롭 반팔 티셔츠", "code": "VF-TP-015",
        "category": "의류", "price": 29000, "discount_price": 24000,
        "options": "화이트 / S, M, L", "stock": 46, "safe_stock": 10, "status": "판매중",
        "registered_at": "2026-09-18", "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=160&auto=format&fit=crop&q=80",
        "description": "탄탄한 코튼 원단과 트렌디한 크롭 기장의 데일리 반팔 티셔츠입니다.",
    },
    {
        "id": "mock-5", "name": "레트로 미니멀 크로스백", "code": "VF-BG-009",
        "category": "가방", "price": 89000, "discount_price": 0,
        "options": "블랙, 브라운", "stock": 0, "safe_stock": 5, "status": "판매중지",
        "registered_at": "2026-09-15", "image": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=160&auto=format&fit=crop&q=80",
        "description": "탄탄한 가죽 소재와 실용적인 수납력을 갖춘 미니멀 크로스백입니다.",
    },
    {
        "id": "mock-6", "name": "빈티지 실버 925 와이드 링", "code": "VF-JW-007",
        "category": "주얼리", "price": 29000, "discount_price": 0,
        "options": "12호, 14호, 16호", "stock": 3, "safe_stock": 5, "status": "판매중",
        "registered_at": "2026-09-12", "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=160&auto=format&fit=crop&q=80",
        "description": "핸드메이드 텍스처를 살린 빈티지 무드의 실버 925 링입니다.",
    },
]

MOCK_INVENTORY_HISTORY = [
    {"id": "movement-1", "product_id": "mock-1", "date": "2026-10-02 14:05", "type": "주문 출고", "quantity": -2, "reason": "주문 VF-20261002-C1P8 출고", "operator": "관리자"},
    {"id": "movement-2", "product_id": "mock-1", "date": "2026-10-01 11:20", "type": "입고", "quantity": 12, "reason": "정기 입고", "operator": "김현우"},
    {"id": "movement-3", "product_id": "mock-2", "date": "2026-10-02 12:42", "type": "재고 조정", "quantity": -1, "reason": "재고 실사 보정", "operator": "관리자"},
    {"id": "movement-4", "product_id": "mock-2", "date": "2026-09-29 09:10", "type": "입고", "quantity": 8, "reason": "신상품 입고", "operator": "박지수"},
    {"id": "movement-5", "product_id": "mock-3", "date": "2026-10-01 16:35", "type": "주문 출고", "quantity": -1, "reason": "주문 VF-20261001-E9T6 출고", "operator": "관리자"},
    {"id": "movement-6", "product_id": "mock-3", "date": "2026-10-01 10:15", "type": "입고", "quantity": 10, "reason": "정기 입고", "operator": "김현우"},
    {"id": "movement-7", "product_id": "mock-4", "date": "2026-10-02 13:18", "type": "주문 출고", "quantity": -3, "reason": "주문 VF-20261002-B7M2 출고", "operator": "관리자"},
    {"id": "movement-8", "product_id": "mock-4", "date": "2026-09-30 15:40", "type": "입고", "quantity": 50, "reason": "시즌 상품 입고", "operator": "박지수"},
    {"id": "movement-9", "product_id": "mock-5", "date": "2026-10-01 17:30", "type": "주문 출고", "quantity": -1, "reason": "주문 출고", "operator": "관리자"},
    {"id": "movement-10", "product_id": "mock-5", "date": "2026-09-27 13:05", "type": "입고", "quantity": 20, "reason": "정기 입고", "operator": "김현우"},
    {"id": "movement-11", "product_id": "mock-6", "date": "2026-10-01 10:40", "type": "재고 조정", "quantity": -2, "reason": "파손/분실", "operator": "관리자"},
    {"id": "movement-12", "product_id": "mock-6", "date": "2026-09-26 12:00", "type": "입고", "quantity": 15, "reason": "상품 입고", "operator": "박지수"},
]


def _get_admin_service_client():
    user_id = session.get("user_id")
    if not user_id:
        abort(401)

    profile = (
        get_supabase_client()
        .table("profiles")
        .select("role")
        .eq("id", user_id)
        .limit(1)
        .execute()
    )
    if not profile.data or profile.data[0].get("role") != "admin":
        abort(403)

    service_client = get_supabase_service_client()
    if not service_client:
        abort(503, description="회원 정보를 조회할 수 없습니다. 관리자 서버 설정을 확인해 주세요.")
    return service_client


def _member_purchase_stats(orders, refunds):
    valid_statuses = {"paid", "preparing", "shipping", "delivered"}
    refunded_by_order = {}
    for refund in refunds:
        if refund.get("status") in {"approved", "completed"}:
            order_id = refund.get("order_id")
            refunded_by_order[order_id] = refunded_by_order.get(order_id, 0) + int(refund.get("refund_amount") or 0)

    order_count = 0
    total_spent = 0
    for order in orders:
        if order.get("status") in valid_statuses:
            order_count += 1
            amount = int(order.get("final_amount") or order.get("total_amount") or 0)
            total_spent += max(0, amount - refunded_by_order.get(order.get("id"), 0))
    return order_count, total_spent


@admin_bp.route('/members')
def members():
    if not session.get("user_id"):
        return redirect(url_for("auth.login", error="login_required"))

    data_error = None
    member_rows = []
    try:
        supabase = _get_admin_service_client()
        profiles = (
            supabase.table("profiles")
            .select("id, email, full_name, phone, grade, total_spent, status, created_at, role")
            .eq("role", "customer")
            .order("created_at", desc=True)
            .execute()
            .data
            or []
        )
        orders = (
            supabase.table("orders")
            .select("id, user_id, status, total_amount, final_amount")
            .execute()
            .data
            or []
        )
        refunds = (
            supabase.table("refunds")
            .select("order_id, status, refund_amount")
            .execute()
            .data
            or []
        )

        orders_by_member = {}
        for order in orders:
            if order.get("user_id"):
                orders_by_member.setdefault(order["user_id"], []).append(order)
        refunds_by_order = {}
        for refund in refunds:
            refunds_by_order.setdefault(refund.get("order_id"), []).append(refund)

        for profile in profiles:
            member_orders = orders_by_member.get(profile["id"], [])
            member_refunds = [
                refund
                for order in member_orders
                for refund in refunds_by_order.get(order.get("id"), [])
            ]
            order_count, total_spent = _member_purchase_stats(member_orders, member_refunds)
            member_rows.append({
                "id": profile["id"],
                "name": profile.get("full_name") or "이름 미등록",
                "email": profile.get("email") or "",
                "phone": profile.get("phone") or "",
                "grade": profile.get("grade") or "BRONZE",
                "order_count": order_count,
                "total_spent": total_spent,
                "created_at": profile.get("created_at"),
                "status": profile.get("status") or "active",
            })
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 회원 목록 조회에 실패했습니다.")
        data_error = "회원 정보를 불러오지 못했습니다. Supabase 연결 및 관리자 권한을 확인해 주세요."

    return render_template(
        'admin/members.html',
        members=member_rows,
        data_error=data_error,
        today_label=datetime.now().strftime("%Y.%m.%d"),
    )


@admin_bp.route('/api/members/<uuid:member_id>')
def member_detail(member_id):
    supabase = _get_admin_service_client()
    member_id = str(member_id)
    profile_result = (
        supabase.table("profiles")
        .select("*")
        .eq("id", member_id)
        .eq("role", "customer")
        .limit(1)
        .execute()
    )
    if not profile_result.data:
        abort(404)

    profile = profile_result.data[0]
    orders = (
        supabase.table("orders")
        .select("id, order_number, status, total_amount, final_amount, created_at")
        .eq("user_id", member_id)
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )
    order_ids = [order["id"] for order in orders]
    order_items = []
    if order_ids:
        order_items = (
            supabase.table("order_items")
            .select("order_id, product_name, option_info, quantity, subtotal")
            .in_("order_id", order_ids)
            .execute()
            .data
            or []
        )
    refunds = (
        supabase.table("refunds")
        .select("id, order_id, status, reason, refund_amount, created_at")
        .eq("user_id", member_id)
        .order("created_at", desc=True)
        .execute()
        .data
        or []
    )
    items_by_order = {}
    for item in order_items:
        items_by_order.setdefault(item.get("order_id"), []).append(item)
    order_by_id = {order.get("id"): order for order in orders}

    order_count, total_spent = _member_purchase_stats(orders, refunds)
    detail_orders = []
    for order in orders:
        detail_orders.append({
            **order,
            "items": items_by_order.get(order.get("id"), []),
        })

    return jsonify({
        "member": {
            "id": member_id,
            "name": profile.get("full_name") or "이름 미등록",
            "email": profile.get("email") or "",
            "phone": profile.get("phone") or "",
            "grade": profile.get("grade") or "BRONZE",
            "created_at": profile.get("created_at"),
            "status": profile.get("status") or "active",
            "points": profile.get("points"),
            "admin_memo": profile.get("admin_memo") or "",
            "order_count": order_count,
            "total_spent": total_spent,
        },
        "orders": detail_orders,
        "refunds": [
            {
                **refund,
                "order_number": order_by_id.get(refund.get("order_id"), {}).get("order_number", "주문 정보 없음"),
                "type": "교환" if "교환" in (refund.get("reason") or "") else "반품/환불",
            }
            for refund in refunds
        ],
    })


@admin_bp.route('/api/members/<uuid:member_id>/memo', methods=['PATCH'])
def update_member_memo(member_id):
    supabase = _get_admin_service_client()
    payload = request.get_json(silent=True) or {}
    memo = payload.get("memo")
    if not isinstance(memo, str) or len(memo) > 1000:
        return jsonify({"success": False, "message": "관리자 메모는 1,000자 이내로 입력해 주세요."}), 400

    result = (
        supabase.table("profiles")
        .update({"admin_memo": memo.strip()})
        .eq("id", str(member_id))
        .eq("role", "customer")
        .execute()
    )
    if not result.data:
        abort(404)
    return jsonify({"success": True, "message": "관리자 메모를 저장했습니다."})


def _return_type(refund):
    request_type = refund.get("request_type")
    if request_type in {"return", "exchange"}:
        return request_type
    return "exchange" if "교환" in (refund.get("reason") or "") else "return"


def _return_status_label(refund):
    if refund.get("status") == "rejected":
        return "거절"
    if refund.get("status") == "completed":
        return "처리 완료"
    if refund.get("status") == "requested":
        return "승인 대기"
    if refund.get("collection_status") != "completed":
        return "회수 대기"
    if refund.get("inspection_status") != "completed":
        return "검수 대기"
    if _return_type(refund) == "exchange":
        return "교환 재배송" if refund.get("redelivery_status") != "shipped" else "처리 대기"
    return "환불 대기" if refund.get("refund_status") != "completed" else "처리 대기"


def _serialize_return(refund, order, member, order_items):
    target_items = order_items
    if refund.get("order_item_id") is not None:
        target_items = [item for item in order_items if str(item.get("id")) == str(refund["order_item_id"])]
    product_names = [item.get("product_name") or "상품 정보 없음" for item in target_items]
    created_at = refund.get("created_at") or ""
    return {
        "id": refund.get("id"),
        "number": f"RT-{int(refund.get('id') or 0):06d}",
        "order_id": (order or {}).get("id"),
        "order_number": (order or {}).get("order_number") or "주문 정보 없음",
        "member_id": (member or {}).get("id") or refund.get("user_id"),
        "member_name": (member or {}).get("full_name") or (order or {}).get("recipient_name") or "회원 정보 없음",
        "member_email": (member or {}).get("email") or "",
        "member_phone": (member or {}).get("phone") or (order or {}).get("recipient_phone") or "",
        "product": ", ".join(product_names) or "상품 정보 없음",
        "type": _return_type(refund),
        "reason": refund.get("reason") or "사유 미입력",
        "customer_request": refund.get("customer_request") or "",
        "requested_option": refund.get("requested_option") or "",
        "refund_amount": int(refund.get("refund_amount") or 0),
        "created_at": created_at,
        "status": refund.get("status") or "requested",
        "status_label": _return_status_label(refund),
        "collection_status": refund.get("collection_status") or "pending",
        "inspection_status": refund.get("inspection_status") or "pending",
        "refund_status": refund.get("refund_status") or "pending",
        "redelivery_status": refund.get("redelivery_status") or "pending",
    }


def _admin_catalog(supabase):
    category_rows = supabase.table("categories").select("id, name").order("display_order").execute().data or []
    category_names = {row["id"]: row["name"] for row in category_rows}
    product_rows = supabase.table("products").select(
        "id, category_id, name, description, price, sale_price, is_active, created_at"
    ).order("created_at", desc=True).execute().data or []
    option_rows = supabase.table("product_options").select(
        "id, product_id, color, size, extra_price, stock_quantity, safe_stock, sku"
    ).execute().data or []
    image_rows = supabase.table("product_images").select(
        "id, product_id, image_url, is_thumbnail, display_order"
    ).order("display_order").execute().data or []
    options_by_product = {}
    images_by_product = {}
    for option in option_rows:
        options_by_product.setdefault(option["product_id"], []).append(option)
    for image in image_rows:
        images_by_product.setdefault(image["product_id"], []).append(image)

    products = []
    for row in product_rows:
        options = options_by_product.get(row["id"], [])
        images = images_by_product.get(row["id"], [])
        sale_price = int(row.get("sale_price") or 0)
        products.append({
            "id": row["id"],
            "name": row.get("name") or "상품명 없음",
            "code": next((option.get("sku") for option in options if option.get("sku")), f"P-{row['id']}"),
            "category": category_names.get(row.get("category_id"), "미분류"),
            "price": int(row.get("price") or 0),
            "discount_price": sale_price,
            "options": ", ".join(" / ".join(str(value) for value in (option.get("color"), option.get("size")) if value) for option in options) or "기본 옵션",
            "option_rows": options,
            "stock": sum(int(option.get("stock_quantity") or 0) for option in options),
            "safe_stock": sum(int(option.get("safe_stock") or 0) for option in options),
            "status": "판매중" if row.get("is_active") else "판매중지",
            "registered_at": str(row.get("created_at") or "")[:10],
            "image": next((image.get("image_url") for image in images if image.get("is_thumbnail")), images[0].get("image_url") if images else ""),
            "description": row.get("description") or "",
        })
    return products, category_rows


def _save_product(supabase, payload, product_id=None):
    name = str(payload.get("name") or "").strip()
    code = str(payload.get("code") or "").strip()
    category = str(payload.get("category") or "").strip()
    image_url = str(payload.get("image") or "").strip()
    description = str(payload.get("description") or "").strip()
    price = payload.get("price")
    discount_price = payload.get("discount_price")
    if not name or not code or not category or not image_url:
        raise ValueError("상품명, 상품코드, 카테고리, 이미지 URL을 입력해 주세요.")
    try:
        price = int(price)
        discount_price = int(discount_price or 0)
        safe_stock = max(0, int(payload.get("safe_stock", 5)))
        initial_stock = max(0, int(payload.get("stock", 0)))
    except (TypeError, ValueError) as error:
        raise ValueError("가격과 재고는 0 이상의 숫자로 입력해 주세요.") from error
    if price < 0 or discount_price < 0 or discount_price > price:
        raise ValueError("할인 가격은 판매가격 이하로 입력해 주세요.")

    category_result = supabase.table("categories").select("id").eq("name", category).limit(1).execute()
    if category_result.data:
        category_id = category_result.data[0]["id"]
    else:
        category_result = supabase.table("categories").insert({
            "name": category,
            "slug": f"category-{uuid.uuid4().hex[:12]}",
        }).execute()
        category_id = category_result.data[0]["id"]

    product_data = {
        "name": name,
        "category_id": category_id,
        "description": description,
        "price": price,
        "sale_price": discount_price or None,
        "is_active": payload.get("status", "판매중") == "판매중",
    }
    if product_id is None:
        saved = supabase.table("products").insert(product_data).execute()
        product_id = saved.data[0]["id"]
        option_result = supabase.table("product_options").insert({
            "product_id": product_id,
            "color": str(payload.get("options") or "기본 옵션")[:100],
            "size": "FREE",
            "sku": code,
            "stock_quantity": initial_stock,
            "safe_stock": safe_stock,
        }).execute()
    else:
        supabase.table("products").update(product_data).eq("id", product_id).execute()
        options = supabase.table("product_options").select(
            "id, stock_quantity, safe_stock"
        ).eq("product_id", product_id).order("id").execute().data or []
        if options:
            if "stock" in payload:
                desired_stock = initial_stock
                stock_delta = desired_stock - sum(int(option.get("stock_quantity") or 0) for option in options)
                for option in options:
                    if not stock_delta:
                        break
                    option_stock = int(option.get("stock_quantity") or 0)
                    option_delta = stock_delta if stock_delta > 0 else -min(option_stock, abs(stock_delta))
                    if option_delta:
                        supabase.rpc("adjust_inventory", {
                            "target_option_id": option["id"],
                            "quantity_delta": option_delta,
                            "adjustment_reason": "상품 정보 재고 조정",
                            "movement_event_key": f"product-edit:{uuid.uuid4().hex}",
                        }).execute()
                        stock_delta -= option_delta
                if stock_delta:
                    raise ValueError("재고를 요청한 수량으로 변경하지 못했습니다.")
            for index, option in enumerate(options):
                option_data = {"safe_stock": safe_stock // len(options) + (1 if index < safe_stock % len(options) else 0)}
                if index == 0:
                    option_data["sku"] = code
                    option_data["color"] = str(payload.get("options") or "기본 옵션")[:100]
                supabase.table("product_options").update(option_data).eq("id", option["id"]).execute()
        else:
            supabase.table("product_options").insert({
                "product_id": product_id,
                "color": str(payload.get("options") or "기본 옵션")[:100],
                "size": "FREE",
                "sku": code,
                "stock_quantity": initial_stock,
                "safe_stock": safe_stock,
            }).execute()

    existing_images = supabase.table("product_images").select(
        "id, image_url"
    ).eq("product_id", product_id).execute().data or []
    if not any(image.get("image_url") == image_url for image in existing_images):
        if existing_images:
            supabase.table("product_images").update({"is_thumbnail": False}).eq("product_id", product_id).execute()
        supabase.table("product_images").insert({
            "product_id": product_id,
            "image_url": image_url,
            "is_thumbnail": True,
            "display_order": 0,
        }).execute()
    return product_id


def _order_rows(supabase):
    orders = supabase.table("orders").select("*").order("created_at", desc=True).execute().data or []
    order_ids = [order["id"] for order in orders]
    member_ids = list({order.get("user_id") for order in orders if order.get("user_id")})
    items = supabase.table("order_items").select(
        "id, order_id, product_id, option_id, product_name, option_info, quantity, price, subtotal"
    ).in_("order_id", order_ids).execute().data if order_ids else []
    profiles = supabase.table("profiles").select("id, full_name, email, phone").in_("id", member_ids).execute().data if member_ids else []
    items_by_order = {}
    profiles_by_id = {str(profile["id"]): profile for profile in profiles or []}
    for item in items or []:
        items_by_order.setdefault(str(item["order_id"]), []).append(item)
    rows = []
    for order in orders:
        profile = profiles_by_id.get(str(order.get("user_id")), {})
        order_items = items_by_order.get(str(order["id"]), [])
        rows.append({
            **order,
            "member_name": profile.get("full_name") or order.get("recipient_name") or "회원 정보 없음",
            "member_email": profile.get("email") or "",
            "member_phone": profile.get("phone") or order.get("recipient_phone") or "",
            "items": order_items,
            "product_summary": ", ".join(item.get("product_name") or "상품 정보 없음" for item in order_items) or "상품 정보 없음",
        })
    return rows


@admin_bp.route('/returns')
def returns():
    if not session.get("user_id"):
        return redirect(url_for("auth.login", error="login_required"))

    try:
        supabase = _get_admin_service_client()
        refunds = supabase.table("refunds").select("*").order("created_at", desc=True).execute().data or []
        orders = supabase.table("orders").select(
            "id, order_number, user_id, recipient_name, recipient_phone, total_amount, final_amount, status, created_at"
        ).execute().data or []
        profiles = supabase.table("profiles").select("id, full_name, email, phone").execute().data or []
        order_items = supabase.table("order_items").select(
            "id, order_id, product_id, option_id, product_name, option_info, quantity, subtotal"
        ).execute().data or []

        orders_by_id = {str(order.get("id")): order for order in orders}
        profiles_by_id = {str(profile.get("id")): profile for profile in profiles}
        items_by_order = {}
        for item in order_items:
            items_by_order.setdefault(str(item.get("order_id")), []).append(item)
        return_rows = []
        for refund in refunds:
            order = orders_by_id.get(str(refund.get("order_id")))
            member_id = refund.get("user_id") or (order or {}).get("user_id")
            member = profiles_by_id.get(str(member_id))
            linked_items = items_by_order.get(str(refund.get("order_id")), [])
            return_rows.append(_serialize_return(refund, order, member, linked_items))
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 반품/교환 목록 조회에 실패했습니다.")
        return_rows = []
        data_error = "반품/교환 정보를 불러오지 못했습니다. Supabase 연결 및 관리자 권한을 확인해 주세요."
    else:
        data_error = None

    return render_template(
        'admin/returns.html',
        returns=return_rows,
        data_error=data_error,
        today_label=datetime.now().strftime("%Y.%m.%d"),
    )


@admin_bp.route('/api/returns/<int:return_id>')
def return_detail(return_id):
    supabase = _get_admin_service_client()
    refund_result = supabase.table("refunds").select("*").eq("id", return_id).limit(1).execute()
    if not refund_result.data:
        abort(404)
    refund = refund_result.data[0]
    order_result = supabase.table("orders").select(
        "id, order_number, user_id, recipient_name, recipient_phone, shipping_address, total_amount, final_amount, status, created_at"
    ).eq("id", refund.get("order_id")).limit(1).execute()
    order = order_result.data[0] if order_result.data else None
    member_id = refund.get("user_id") or (order or {}).get("user_id")
    member_result = supabase.table("profiles").select(
        "id, full_name, email, phone"
    ).eq("id", member_id).limit(1).execute() if member_id else None
    member = member_result.data[0] if member_result and member_result.data else None
    item_query = supabase.table("order_items").select(
        "id, order_id, product_id, option_id, product_name, option_info, quantity, subtotal"
    ).eq("order_id", refund.get("order_id"))
    order_items = item_query.execute().data or []
    detail = _serialize_return(refund, order, member, order_items)
    if refund.get("order_item_id") is not None:
        order_items = [item for item in order_items if str(item.get("id")) == str(refund["order_item_id"])]

    exchange_stock = []
    if detail["type"] == "exchange":
        product_ids = {item.get("product_id") for item in order_items if item.get("product_id") is not None}
        for product_id in product_ids:
            stock_rows = supabase.table("product_options").select(
                "id, product_id, color, size, stock_quantity, safe_stock, sku"
            ).eq("product_id", product_id).execute().data or []
            exchange_stock.extend(stock_rows)

    return jsonify({
        "request": detail,
        "order": order or {},
        "member": member or {},
        "products": order_items,
        "exchange_stock": exchange_stock,
    })


@admin_bp.route('/api/returns/<int:return_id>/action', methods=['PATCH'])
def update_return_status(return_id):
    supabase = _get_admin_service_client()
    payload = request.get_json(silent=True) or {}
    action = payload.get("action")
    refund_result = supabase.table("refunds").select("*").eq("id", return_id).limit(1).execute()
    if not refund_result.data:
        abort(404)
    refund = refund_result.data[0]
    request_type = _return_type(refund)
    status = refund.get("status") or "requested"
    collection_status = refund.get("collection_status") or "pending"
    inspection_status = refund.get("inspection_status") or "pending"
    refund_status = refund.get("refund_status") or "pending"
    redelivery_status = refund.get("redelivery_status") or "pending"
    updates = {}

    if action in {"approve", "reject"} and status == "requested":
        updates["status"] = "approved" if action == "approve" else "rejected"
    elif action == "collection_complete" and status == "approved" and collection_status != "completed":
        updates["collection_status"] = "completed"
    elif action == "inspection_complete" and status == "approved" and collection_status == "completed" and inspection_status != "completed":
        updates["inspection_status"] = "completed"
    elif action == "refund_complete" and request_type == "return" and status == "approved" and inspection_status == "completed" and refund_status != "completed":
        updates["refund_status"] = "completed"
        updates["processed_at"] = datetime.now().astimezone().isoformat()
    elif action == "redelivery" and request_type == "exchange" and status == "approved" and inspection_status == "completed" and redelivery_status != "shipped":
        try:
            requested_option_id = int(payload.get("option_id"))
        except (TypeError, ValueError):
            return jsonify({"success": False, "message": "재배송할 교환 옵션을 선택해 주세요."}), 400
        order_item_query = supabase.table("order_items").select("product_id").eq("order_id", refund.get("order_id"))
        if refund.get("order_item_id") is not None:
            order_item_query = order_item_query.eq("id", refund["order_item_id"])
        requested_items = order_item_query.execute().data or []
        eligible_product_ids = {item.get("product_id") for item in requested_items}
        option_result = supabase.table("product_options").select(
            "id, product_id, color, size, stock_quantity"
        ).eq("id", requested_option_id).limit(1).execute()
        if not option_result.data or option_result.data[0].get("product_id") not in eligible_product_ids:
            return jsonify({"success": False, "message": "교환 상품 옵션을 확인할 수 없습니다."}), 400
        if int(option_result.data[0].get("stock_quantity") or 0) < 1:
            return jsonify({"success": False, "message": "선택한 교환 옵션의 재고가 부족합니다."}), 409
        option = option_result.data[0]
        updates["requested_option_id"] = requested_option_id
        updates["requested_option"] = " / ".join(value for value in (option.get("color"), option.get("size")) if value) or option.get("sku") or "선택 옵션"
        updates["redelivery_status"] = "shipped"
    elif action == "complete" and status == "approved" and (
        (request_type == "return" and refund_status == "completed")
        or (request_type == "exchange" and redelivery_status == "shipped")
    ):
        updates["status"] = "completed"
        updates["processed_at"] = datetime.now().astimezone().isoformat()

    if not updates:
        return jsonify({"success": False, "message": "현재 단계에서 처리할 수 없는 요청입니다."}), 409

    updated = supabase.table("refunds").update(updates).eq("id", return_id).execute()
    if not updated.data:
        return jsonify({"success": False, "message": "상태 변경 내용을 저장하지 못했습니다."}), 500
    return jsonify({"success": True, "message": "처리 상태를 변경했습니다.", "refund": updated.data[0]})


@admin_bp.route('/')
def dashboard():
    data_error = None
    metrics = []
    revenue = []
    order_statuses = []
    recent_orders = []
    recent_returns = []
    try:
        supabase = _get_admin_service_client()
        orders = _order_rows(supabase)
        today = datetime.now().date()
        status_labels = {"paid": "결제완료", "preparing": "상품준비", "shipping": "배송중", "delivered": "배송완료", "cancelled": "취소", "refunded": "환불", "pending": "결제대기"}
        status_classes = {"paid": "paid", "preparing": "preparing", "shipping": "shipping", "delivered": "delivered", "cancelled": "cancelled", "refunded": "cancelled", "pending": "preparing"}
        status_counts = {}
        sales_by_day = {}
        for order in orders:
            status_counts[order.get("status")] = status_counts.get(order.get("status"), 0) + 1
            created = str(order.get("created_at") or "")[:10]
            if created:
                sales_by_day[created] = sales_by_day.get(created, 0) + (int(order.get("final_amount") or 0) if order.get("status") not in {"cancelled", "refunded"} else 0)
        today_orders = [order for order in orders if str(order.get("created_at") or "")[:10] == today.isoformat()]
        today_sales = sum(int(order.get("final_amount") or 0) for order in today_orders if order.get("status") not in {"cancelled", "refunded"})
        queued = sum(1 for order in orders if order.get("status") in {"paid", "preparing"})
        products, _ = _admin_catalog(supabase)
        near_stock_count = sum(1 for product in products if product["stock"] <= product["safe_stock"])
        member_count = len(supabase.table("profiles").select("id").eq("role", "customer").execute().data or [])
        refunds = supabase.table("refunds").select("*").order("created_at", desc=True).limit(10).execute().data or []
        order_statuses = [
            {"label": label, "count": status_counts.get(status, 0), "color": color}
            for status, label, color in [("paid", "결제완료", "#4f83ed"), ("preparing", "상품준비", "#76a5f5"), ("shipping", "배송중", "#54b8c7"), ("delivered", "배송완료", "#55b58b"), ("cancelled", "취소", "#b6c0ce")]
        ]
        metrics = [
            {"title": "오늘 주문", "value": f"{len(today_orders):,}건", "change": "실시간", "trend": "good", "icon": "bi-bag-check", "tone": "blue"},
            {"title": "오늘 매출", "value": f"₩{today_sales:,}", "change": "실시간", "trend": "good", "icon": "bi-credit-card", "tone": "sky"},
            {"title": "배송 대기", "value": f"{queued:,}건", "change": "현재", "trend": "good", "icon": "bi-truck", "tone": "amber"},
            {"title": "반품/교환 접수", "value": f"{sum(1 for row in refunds if row.get('status') == 'requested'):,}건", "change": "현재", "trend": "good", "icon": "bi-arrow-left-right", "tone": "violet"},
            {"title": "전체 회원", "value": f"{member_count:,}명", "change": "현재", "trend": "good", "icon": "bi-person-lines-fill", "tone": "teal"},
            {"title": "품절 임박 상품", "value": f"{near_stock_count:,}개", "change": "현재", "trend": "bad" if near_stock_count else "good", "icon": "bi-exclamation-circle", "tone": "rose"},
        ]
        for offset in range(6, -1, -1):
            day = today - timedelta(days=offset)
            revenue.append({"label": f"{day.month}/{day.day}", "amount": sales_by_day.get(day.isoformat(), 0)})
        recent_orders = [{
            "number": order.get("order_number"),
            "date": str(order.get("created_at") or "")[:16].replace("T", " ").replace("-", "."),
            "member": order["member_name"],
            "product": order["product_summary"],
            "amount": int(order.get("final_amount") or 0),
            "status": status_labels.get(order.get("status"), order.get("status", "확인 필요")),
            "status_class": status_classes.get(order.get("status"), "cancelled"),
            "id": order.get("id"),
        } for order in orders[:7]]
        order_by_id = {str(order.get("id")): order for order in orders}
        profile_rows = supabase.table("profiles").select("id, full_name").execute().data or []
        profile_names = {str(profile["id"]): profile.get("full_name") or "회원 정보 없음" for profile in profile_rows}
        item_rows = supabase.table("order_items").select("order_id, product_name").execute().data or []
        items_by_order = {}
        for item in item_rows:
            items_by_order.setdefault(str(item.get("order_id")), []).append(item.get("product_name") or "상품 정보 없음")
        for refund in refunds[:4]:
            order = order_by_id.get(str(refund.get("order_id")), {})
            refund_type = _return_type(refund)
            label = _return_status_label(refund)
            recent_returns.append({
                "number": f"RT-{int(refund.get('id') or 0):06d}",
                "order": order.get("order_number") or "주문 정보 없음",
                "member": profile_names.get(str(refund.get("user_id")), order.get("recipient_name", "회원 정보 없음")),
                "product": ", ".join(items_by_order.get(str(refund.get("order_id")), [])),
                "type": "교환" if refund_type == "exchange" else "반품",
                "status": label,
                "status_class": "completed" if refund.get("status") == "completed" else "processing",
            })
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 대시보드 데이터를 불러오지 못했습니다.")
        data_error = "대시보드 데이터를 불러오지 못했습니다. Supabase 연결과 관리자 권한을 확인해 주세요."

    return render_template(
        'admin/dashboard.html',
        metrics=metrics,
        revenue=revenue,
        order_statuses=order_statuses,
        recent_orders=recent_orders,
        recent_returns=recent_returns,
        data_error=data_error,
        today_label=datetime.now().strftime("%Y.%m.%d"),
    )


@admin_bp.route('/products')
def products():
    try:
        products, category_rows = _admin_catalog(_get_admin_service_client())
        categories = sorted({category["name"] for category in category_rows})
        data_error = None
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 상품 목록 조회에 실패했습니다.")
        products, categories = [], []
        data_error = "상품 정보를 불러오지 못했습니다. Supabase 연결과 관리자 권한을 확인해 주세요."
    return render_template(
        'admin/products.html',
        products=products,
        categories=categories,
        data_error=data_error,
        today_label=datetime.now().strftime("%Y.%m.%d"),
    )


@admin_bp.route('/inventory')
def inventory():
    try:
        supabase = _get_admin_service_client()
        products, _ = _admin_catalog(supabase)
        movement_rows = supabase.table("inventory_movements").select("*").order("created_at", desc=True).limit(300).execute().data or []
        movement_labels = {"order": "주문 출고", "cancel_restock": "주문 취소 입고", "return_restock": "반품 입고", "exchange_restock": "교환 회수 입고", "exchange_out": "교환 재배송", "adjustment": "재고 조정"}
        inventory_history = [{
            "id": movement.get("id"),
            "product_id": str(movement.get("product_id") or ""),
            "date": str(movement.get("created_at") or "")[:16].replace("T", " "),
            "type": movement_labels.get(movement.get("movement_type"), "재고 변동"),
            "quantity": int(movement.get("quantity") or 0),
            "reason": movement.get("reason") or "",
            "operator": "관리자" if movement.get("movement_type") == "adjustment" else "시스템",
        } for movement in movement_rows]
        data_error = None
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 재고 목록 조회에 실패했습니다.")
        products, inventory_history = [], []
        data_error = "재고 정보를 불러오지 못했습니다. 스키마 적용과 관리자 권한을 확인해 주세요."
    return render_template(
        'admin/inventory.html',
        products=products,
        inventory_history=inventory_history,
        data_error=data_error,
        today_label=datetime.now().strftime("%Y.%m.%d"),
    )


@admin_bp.route('/orders')
def orders():
    try:
        order_rows = _order_rows(_get_admin_service_client())
        data_error = None
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 주문 목록 조회에 실패했습니다.")
        order_rows = []
        data_error = "주문 정보를 불러오지 못했습니다. Supabase 연결과 관리자 권한을 확인해 주세요."
    return render_template('admin/orders.html', orders=order_rows, data_error=data_error, today_label=datetime.now().strftime("%Y.%m.%d"))


@admin_bp.route('/api/products', methods=['GET', 'POST'])
def create_product():
    try:
        supabase = _get_admin_service_client()
        if request.method == 'GET':
            products, categories = _admin_catalog(supabase)
            return jsonify({"products": products, "categories": [row["name"] for row in categories]})
        product_id = _save_product(supabase, request.get_json(silent=True) or {})
        return jsonify({"success": True, "product_id": product_id}), 201
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception:
        logging.exception("관리자 상품 생성에 실패했습니다.")
        return jsonify({"success": False, "message": "상품을 저장하지 못했습니다. 입력값과 스키마를 확인해 주세요."}), 500


@admin_bp.route('/api/products/<int:product_id>', methods=['PATCH', 'DELETE'])
def update_or_delete_product(product_id):
    try:
        supabase = _get_admin_service_client()
        if request.method == 'DELETE':
            deleted = supabase.table("products").delete().eq("id", product_id).execute()
            if not deleted.data:
                abort(404)
            return jsonify({"success": True})
        _save_product(supabase, request.get_json(silent=True) or {}, product_id=product_id)
        return jsonify({"success": True})
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 상품 변경에 실패했습니다.")
        return jsonify({"success": False, "message": "상품을 변경하지 못했습니다."}), 500


@admin_bp.route('/api/inventory/options/<int:option_id>/adjust', methods=['PATCH'])
def adjust_inventory(option_id):
    try:
        supabase = _get_admin_service_client()
        payload = request.get_json(silent=True) or {}
        delta = int(payload.get("delta"))
        reason = str(payload.get("reason") or "").strip()
        if delta == 0 or not reason:
            return jsonify({"success": False, "message": "변경 수량과 조정 사유를 입력해 주세요."}), 400
        option_result = supabase.table("product_options").select("product_id").eq("id", option_id).limit(1).execute()
        if not option_result.data:
            abort(404)
        result = supabase.rpc("adjust_inventory", {
            "target_option_id": option_id,
            "quantity_delta": delta,
            "adjustment_reason": reason,
            "movement_event_key": f"admin-adjust:{uuid.uuid4().hex}",
        }).execute()
        products, _ = _admin_catalog(supabase)
        movement_type = "입고" if delta > 0 else "재고 조정"
        movement = {
            "id": uuid.uuid4().hex,
            "product_id": str(option_result.data[0]["product_id"]),
            "date": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
            "type": movement_type,
            "quantity": delta,
            "reason": reason,
            "operator": "관리자",
        }
        return jsonify({"success": True, "option": result.data, "products": products, "movement": movement})
    except Exception as error:
        from werkzeug.exceptions import HTTPException
        if isinstance(error, HTTPException):
            raise
        logging.exception("관리자 재고 조정에 실패했습니다.")
        return jsonify({"success": False, "message": "재고가 부족하거나 재고 조정에 실패했습니다."}), 400


@admin_bp.route('/api/orders/<uuid:order_id>')
def order_detail(order_id):
    supabase = _get_admin_service_client()
    order_result = supabase.table("orders").select("*").eq("id", str(order_id)).limit(1).execute()
    if not order_result.data:
        abort(404)
    order = order_result.data[0]
    items = supabase.table("order_items").select(
        "id, product_id, option_id, product_name, option_info, quantity, price, subtotal"
    ).eq("order_id", str(order_id)).execute().data or []
    member_result = supabase.table("profiles").select(
        "id, full_name, email, phone, grade"
    ).eq("id", order.get("user_id")).limit(1).execute() if order.get("user_id") else None
    return jsonify({"order": order, "member": member_result.data[0] if member_result and member_result.data else {}, "items": items})


@admin_bp.route('/api/orders/<uuid:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    supabase = _get_admin_service_client()
    requested_status = (request.get_json(silent=True) or {}).get("status")
    order_result = supabase.table("orders").select("id, status").eq("id", str(order_id)).limit(1).execute()
    if not order_result.data:
        abort(404)
    current_status = order_result.data[0].get("status")
    allowed = {
        "pending": {"paid", "cancelled"},
        "paid": {"preparing", "cancelled"},
        "preparing": {"shipping", "cancelled"},
        "shipping": {"delivered"},
    }
    if requested_status not in allowed.get(current_status, set()):
        return jsonify({"success": False, "message": "현재 주문 상태에서 변경할 수 없는 단계입니다."}), 409
    updated = supabase.table("orders").update({"status": requested_status}).eq("id", str(order_id)).eq("status", current_status).execute()
    if not updated.data:
        return jsonify({"success": False, "message": "주문 상태가 이미 변경되었습니다. 새로고침 후 다시 확인해 주세요."}), 409
    return jsonify({"success": True, "order": updated.data[0]})