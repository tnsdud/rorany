-- ==============================================================================
-- VIBE-FASHION 초기 데이터(Seed) SQL
-- Supabase SQL Editor에서 실행 가능
-- ==============================================================================

-- 1. 카테고리 7개 등록 (상의, 하의, 아우터, 원피스/세트, 액세서리, 가방, 신발)
INSERT INTO public.categories (name, slug, display_order)
VALUES 
    ('상의', 'top', 1),
    ('하의', 'bottom', 2),
    ('아우터', 'outer', 3),
    ('원피스/세트', 'dress', 4),
    ('액세서리', 'acc', 5),
    ('가방', 'bag', 6),
    ('신발', 'shoes', 7)
ON CONFLICT (slug) DO UPDATE 
SET name = EXCLUDED.name, display_order = EXCLUDED.display_order;

-- 2. 샘플 상품 4개 등록
-- 참고: '베이직 크롭 티셔츠'의 정가는 29,900원, 할인가는 19,900원으로 정상 설정 (정가 >= 할인가 제약조건 충족)
INSERT INTO public.products (category_id, name, slug, description, price, sale_price, is_active)
VALUES 
    (
        (SELECT id FROM public.categories WHERE slug = 'top'),
        '베이직 크롭 티셔츠',
        'basic-crop-t-shirt',
        '부드러운 코튼 원사로 제작된 데일리 베이직 크롭 티셔츠입니다.',
        29900,
        19900,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'bottom'),
        '와이드 데님 팬츠',
        'wide-denim-pants',
        '트렌디한 실루엣과 편안한 착용감을 주는 와이드 핏 데님 팬츠입니다.',
        39900,
        NULL,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'outer'),
        '오버핏 코튼 자켓',
        'overfit-cotton-jacket',
        '간절기 시즌 가볍고 멋스럽게 걸치기 좋은 오버핏 코튼 자켓입니다.',
        59900,
        NULL,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'dress'),
        '플로럴 미디 원피스',
        'floral-midi-dress',
        '화사한 플라워 패턴과 페미닌한 라인이 돋보이는 미디 원피스입니다.',
        45900,
        NULL,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'shoes'),
        '클래식 레더 더비 슈즈',
        'classic-leather-derby-shoes',
        '미니멀한 실루엣과 편안한 쿠셔닝을 갖춘 데일리 천연 소가죽 슈즈입니다.',
        145000,
        NULL,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'bag'),
        '레트로 미니멀 크로스백',
        'retro-minimal-crossbag',
        '탄탄한 가죽 소재와 실용적인 수납력을 자랑하는 미니멀 크로스백입니다.',
        89000,
        NULL,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'acc'),
        '14K 골드 도금 볼드 드롭 귀걸이',
        '14k-bold-drop-earrings',
        '은은한 골드 광택과 감각적인 곡선이 돋보이는 모던 드롭 이어링입니다.',
        32000,
        NULL,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'acc'),
        '레이어드 실버 체인 목걸이',
        'layered-silver-chain-necklace',
        '모던한 두 줄 레이어드로 다양한 스타일에 포인트가 되는 실버 네크리스입니다.',
        38000,
        NULL,
        true
    ),
    (
        (SELECT id FROM public.categories WHERE slug = 'acc'),
        '빈티지 실버 925 와이드 링',
        'vintage-silver-925-wide-ring',
        '볼드하면서도 감성적인 텍스처를 살린 핸드메이드 실버 925 반지입니다.',
        29000,
        NULL,
        true
    )
ON CONFLICT (slug) DO UPDATE 
SET 
    category_id = EXCLUDED.category_id,
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price = EXCLUDED.price,
    sale_price = EXCLUDED.sale_price,
    is_active = EXCLUDED.is_active;

-- 3. 첫 번째 상품(베이직 크롭 티셔츠) 옵션 9개 등록 (블랙/화이트/베이지 × S/M/L)
WITH target_product AS (
    SELECT id FROM public.products WHERE slug = 'basic-crop-t-shirt' LIMIT 1
)
INSERT INTO public.product_options (product_id, color, size, extra_price, stock_quantity, sku)
SELECT 
    target_product.id,
    opts.color,
    opts.size,
    0,
    opts.stock,
    'TOP-CROP-' || UPPER(opts.color_code) || '-' || opts.size
FROM target_product
CROSS JOIN (
    VALUES 
        ('블랙', 'BLK', 'S', 50),
        ('블랙', 'BLK', 'M', 50),
        ('블랙', 'BLK', 'L', 30),
        ('화이트', 'WHT', 'S', 50),
        ('화이트', 'WHT', 'M', 50),
        ('화이트', 'WHT', 'L', 30),
        ('베이지', 'BEG', 'S', 30),
        ('베이지', 'BEG', 'M', 40),
        ('베이지', 'BEG', 'L', 20)
) AS opts(color, color_code, size, stock);

-- 4. 샘플 상품 대표 이미지 등록 (Unsplash 패션 고화질 이미지)
INSERT INTO public.product_images (product_id, image_url, is_thumbnail, display_order)
VALUES 
    (
        (SELECT id FROM public.products WHERE slug = 'basic-crop-t-shirt'),
        'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = 'wide-denim-pants'),
        'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = 'overfit-cotton-jacket'),
        'https://images.unsplash.com/photo-1548883354-7622d03aca27?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = 'floral-midi-dress'),
        'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = 'classic-leather-derby-shoes'),
        'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = 'retro-minimal-crossbag'),
        'https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = '14k-bold-drop-earrings'),
        'https://images.unsplash.com/photo-1630019852942-f89202989a59?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = 'layered-silver-chain-necklace'),
        'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop&q=80',
        true,
        1
    ),
    (
        (SELECT id FROM public.products WHERE slug = 'vintage-silver-925-wide-ring'),
        'https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop&q=80',
        true,
        1
    );
