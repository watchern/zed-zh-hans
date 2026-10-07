<!--ChatGPT-4o에 의해 번역됨-->
<!---![zed](https://avatars.githubusercontent.com/u/79345384?s=200&v=4)--->
# 🌏 zed-loc (Zed 현지화)
 [![GitHub issues][issues-image]][issues-url]
 [![Github Pulls][pulls-image]][pulls-url]
 [![GitHub stars][stars-image]][stars-url]
 [![GitHub forks][forks-image]][forks-url]
 [![Github Downloads][download-image]][download-url]
 [![license][license-image]][license-url]
 ![repo-size][repo-size-image]

[简体中文](README.md)|[English](README.en.md)|[日本語](README.ja.md)|**한국어**

## 프로젝트 개요

`zed-loc`은 [Zed 편집기](https://github.com/zed-industries/zed)의 현지화를 위한 도구입니다. 이 도구는 소스 코드에서 문자열을 추출하여 JSON 파일을 생성하며, 이를 번역 및 현지화에 사용할 수 있습니다. 또한 자동 빌드 및 배포 기능을 지원합니다.

## 기능

- 소스 코드에서 문자열 자동 추출
- 번역을 용이하게 하는 JSON 파일 생성
- GitHub Actions 통합, 자동 빌드 및 배포 지원
- 현재 매일 밤 수동으로 현지화 빌드를 실행 중

## 실행
### 구성
Python3 및 Rust가 설치되어 있는지 확인하십시오.

다음 명령어를 실행해 프로젝트를 클론하거나 상단 오른쪽의 "코드" 버튼을 클릭해 압축 파일을 다운로드하세요:

```bash
git clone https://github.com/tc999/zed-loc.git
cd zed-loc
```
### 문자열 추출

> [!note]
>
> 주의: 문자열 추출은 Windows 시스템에서만 실행 가능합니다. Linux와 MacOS에서는 오류가 발생합니다.

먼저 Zed 소스 코드를 로컬에 동기화해야 합니다:

```bash
git clone https://github.com/zed-industries/zed.git
```

이후 문자열을 추출하며, 기본적으로 `strings.json` 파일에 저장합니다:
```bash
python3 step1-extract.py
```
불필요한 문자열을 삭제하는 규칙은 `del.yaml` 파일에 저장되어 있습니다:
```bash
python3 step2-delete.py
```

### 문자열 번역
> [!caution]
>
> 경고: 추출 스크립트는 모든 따옴표 안의 내용을 추출하므로, 번역 시 Zed 소스 코드를 참고하며 번역해야 합니다. 번역이 필요 없는 내용은 삭제하십시오.

번역 방법: GPT를 사용해 기계 번역한 후 수동으로 수정합니다.

`strings.json` 파일을 대상 언어 코드 이름으로 새로 저장한 후, 번역이 완료되면 다음 명령어를 실행하여 문자열을 교체합니다:
```bash
python3 step4-replace.py ko\ko-KR.json
```

### 빌드
컴파일 오류가 발생하면 Zed 소스 코드를 삭제한 후 다시 클론하십시오:

```bash
cd zed
cargo run
```

정상적으로 컴파일되고 실행되는지 확인하세요.

# 감사의 말씀

- [Zed](https://github.com/zed-industries/zed) - Zed 편집기의 모든 기여자들
- [deevus/zed-windows-builds](https://github.com/deevus/zed-windows-builds) - Zed Windows 빌드 스크립트 참고
- [Nriver/zed-translation](https://github.com/Nriver/zed-translation) - 아이디어 제공
- [GitHub Copilot](https://github.com/copilot) - 스크립트 작성 지원

## 모든 기여자에게 감사드립니다

언제나 멋진 기여자들에게 감사드립니다 ❤️!

<a href="https://github.com/TC999" title="陈生杂物房">
  <img src="https://avatars.githubusercontent.com/u/88823709?v=4" width="42;" alt="陈生杂物房"/>
</a>
<a href="https://github.com/shenjackyuanjie" title="shenjack">
  <img src="https://avatars.githubusercontent.com/u/54507071?v=4" width="42;" alt="shenjack"/>
</a>
<a href="https://github.com/oper0" title="oper0">
  <img src="https://avatars.githubusercontent.com/u/204131036?v=4" width="42;" alt="oper0"/>
</a>

# 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)에 따라 공개되며, 모든 조직과 개인이 무료로 사용할 수 있습니다.

[issues-url]: https://github.com/TC999/zed-loc/issues "이슈"
[issues-image]: https://img.shields.io/github/issues/TC999/zed-loc?style=flat-square&logo=github&label=이슈

[pulls-url]: https://github.com/TC999/zed-loc/pulls "풀 리퀘스트"
[pulls-image]: https://img.shields.io/github/issues-pr-raw/TC999/zed-loc?style=flat&logo=github&%3Fcolor%3Dgreen&label=풀+리퀘스트

[stars-url]: https://github.com/TC999/zed-loc/stargazers "스타"
[stars-image]: https://img.shields.io/github/stars/TC999/zed-loc?style=flat-square&logo=github&label=스타"

[forks-url]: https://github.com/TC999/zed-loc/fork "포크"
[forks-image]: https://img.shields.io/github/forks/TC999/zed-loc?style=flat-square&logo=github&label=포크

[discussions-url]: https://github.com/TC999/zed-loc/discussions "토론"

[hits-url]: https://hits.dwyl.com/ "방문 수"
[hits-image]: https://custom-icon-badges.demolab.com/endpoint?url=https%3A%2F%2Fhits.dwyl.com%2FTC999%2Fzed-loc.json%3Fcolor%3Dgreen&label=%EB%B0%A9%EB%AC%B8+%EC%88%98&logo=graph

[repo-url]: https://github.com/TC999/zed-loc "저장소 주소"

[repo-size-image]:https://img.shields.io/github/repo-size/TC999/zed-loc?style=flat-square&label=%EC%A0%80%EC%9E%A5%EC%86%8C+%ED%81%AC%EA%B8%B0


[download-url]: https://github.com/TC999/zed-loc/releases/latest "다운로드"
[download-image]: https://img.shields.io/github/downloads/TC999/zed-loc/total?style=flat-square&logo=github&label=%EC%B4%9D+%EB%8B%A4%EC%9A%B4%EB%A1%9C%EB%93%9C+%EC%88%98"

[license-url]: https://github.com/TC999/zed-loc/blob/master/LICENSE "라이선스"
[license-image]: https://custom-icon-badges.demolab.com/github/license/TC999/zed-loc?style=flat&logo=law&label=%EB%9D%BC%EC%9D%B4%EC%84%A0%EC%8A%A4
