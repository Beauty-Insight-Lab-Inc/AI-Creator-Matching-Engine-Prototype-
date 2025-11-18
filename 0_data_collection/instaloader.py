import instaloader
import time

# Instaloader 객체 생성
L = instaloader.Instaloader()

# (선택 사항) 로그인 - 비공개 계정 정보나 더 많은 데이터에 접근하려면 필요하지만,
# 로그인 시 계정 정지 위험이 매우 높아집니다.
# L.login("YOUR_USERNAME", "YOUR_PASSWORD")

# 가상의 프로필 이름
PROFILE_NAME = "some_username"

try:
    # 프로필 객체 가져오기
    profile = instaloader.Profile.from_username(L.context, PROFILE_NAME)

    print(f"--- 프로필: {profile.username} ---")
    print(f"팔로워 수: {profile.followers}")
    print(f"팔로잉 수: {profile.followees}")
    print(f"게시물 수: {profile.mediacount}")
    print(f"바이오: \n{profile.biography}")

    # (참고) '인게이지먼트율'은 Instaloader가 직접 제공하는 항목이 아닙니다.
    # 이를 계산하려면 최근 게시물을 모두 순회하며 '좋아요'와 '댓글' 수를
    # 집계한 후 팔로워 수로 나누는 복잡한 계산이 필요하며,
    # 이는 속도 제한에 걸릴 확률이 매우 높습니다.

    # (참고) '니치 분류'는 바이오 텍스트를 직접 파싱해야 합니다.
    bio_text = profile.biography.lower()
    niches = []
    if "skincare" in bio_text:
        niches.append("스킨케어")
    if "makeup" in bio_text:
        niches.append("메이크업")
    if "haircare" in bio_text:
        niches.append("헤어케어")
    
    print(f"예상 니치: {', '.join(niches) if niches else 'N/A'}")


except instaloader.exceptions.ProfileNotExistsException:
    print(f"오류: 프로필 '{PROFILE_NAME}'을(를) 찾을 수 없습니다.")
except Exception as e:
    print(f"기타 오류 발생: {e}")