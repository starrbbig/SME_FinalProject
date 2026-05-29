# 1. 프로젝트 동기 및 문제 정의

본 프로젝트의 목표는 18개의 Base Station(BS)으로부터 수집된 RTT(Round Trip Time) 거리 측정값을 이용하여 사용자의 2차원 위치를 추정하는 것이다.

RTT 기반 위치 추정의 가장 기본적인 방법은 모든 거리 측정값을 동일하게 신뢰하고 Least Squares(LS)를 적용하는 것이다. 그러나 제공된 데이터를 분석한 결과 RTT 측정값에는 매우 큰 오차가 존재하였으며, 일부 BS는 실제 거리보다 수십 미터 이상 큰 값을 측정하는 경우도 확인되었다.

이러한 현상은 NLOS(Non-Line-of-Sight), Multipath Propagation, 측정 지연 등의 영향으로 발생할 수 있으며, 단순 Least Squares는 이러한 이상치에 매우 민감하게 반응한다.

실제로 Baseline 실험 결과 Mean Error는 23.21 m, Median Error는 21.73 m로 나타났으며, RTT 이상치가 위치 추정 성능을 크게 저하시키는 것을 확인하였다.

따라서 본 프로젝트에서는 단순히 이상치를 제거하는 접근 방식 대신, 현재 위치 추정 결과와 각 BS 측정값의 일관성을 평가하여 센서 신뢰도(Sensor Reliability)를 계산하는 방법을 제안하였다.

또한 RTT 측정값에 존재하는 체계적인 거리 Bias를 보정하고, 위치 추정과 신뢰도 추정을 반복적으로 수행함으로써 강건한 위치 추정을 달성하고자 하였다.

최종적으로 본 프로젝트에서는 Adaptive Iterative Trust-Bias Localization 알고리즘을 제안한다.

---

# 2. 알고리즘 설명

제안하는 알고리즘은 다음 5단계로 구성된다.

1. 초기 강건 위치 추정
2. Residual 분석
3. Sensor Reliability 추정
4. RTT Bias 보정
5. Iterative Refinement

입력으로는 사용자의 RTT 거리 측정값과 18개의 BS 위치가 주어진다.

## 2.1 초기 강건 위치 추정

초기 위치는 Huber Robust Least Squares를 이용하여 계산한다.

일반 Least Squares는 큰 Residual에 매우 민감하므로 초기 위치 추정 단계에서 Huber Loss를 사용하여 이상치의 영향을 완화하였다.

Huber Loss는 작은 Residual 구간에서는 Least Squares와 유사하게 동작하고, 큰 Residual 구간에서는 영향력을 제한함으로써 초기 위치 추정을 안정화한다.

---

## 2.2 Residual 분석

초기 위치가 계산되면 각 BS에 대해 예측 거리와 측정 거리의 차이를 계산한다.

Residual은 다음과 같이 정의한다.

ri = d_pred,i - d_i

여기서

* d_pred,i : 현재 추정 위치에서 계산한 BS i까지의 거리
* d_i : RTT 측정 거리

이다.

Residual 분포를 분석하기 위해 Median과 MAD(Median Absolute Deviation)를 계산한다.

MAD = median(|ri - median(r)|)

MAD는 평균과 표준편차보다 이상치의 영향을 덜 받기 때문에 강건한 분산 추정에 적합하다.

---

## 2.3 Sensor Reliability 추정

Residual이 Median에 가까운 BS는 현재 위치 추정 결과와 일관성이 높다고 판단하였다.

반대로 Residual이 크게 벗어난 BS는 이상치일 가능성이 높다고 판단하였다.

이를 이용하여 각 BS의 신뢰도(Trust Score)를 계산하였다.

Trust Score는 Residual 편차가 증가할수록 비선형적으로 감소하도록 설계하였다.

또한 MAD 기반 Hard Filtering을 적용하여 매우 큰 이상치는 강하게 억제하였다.

본 방법은 센서를 단순히 제거하는 방식이 아니라 모든 센서에 연속적인 신뢰도를 부여한다는 특징을 가진다.

---

## 2.4 RTT Bias 보정

데이터를 분석한 결과 대부분의 BS에서 Residual Median이 양수로 나타났다.

이는 RTT 측정값이 실제 거리보다 체계적으로 크게 측정되는 경향이 존재함을 의미한다.

실제로 18개 BS 전체의 Residual 통계를 분석한 결과 대부분의 BS에서 Residual Median이 양수로 나타났으며, 이는 NLOS와 Multipath 영향으로 인한 RTT 거리 과대 측정 현상으로 해석할 수 있었다.

따라서 단순히 센서 신뢰도만 조정하는 것보다 거리 자체를 보정하는 것이 효과적일 것이라는 가설을 세웠다.

Residual Median을 RTT Bias로 간주하고 거리 측정값 보정에 활용하였다.

Bias 보정은 RTT 측정값 자체를 수정하므로 단순한 신뢰도 조정보다 더 직접적으로 거리 오차를 감소시킬 수 있다.

---

## 2.5 Iterative Refinement

보정된 RTT를 이용하여 다시 위치를 추정한다.

새로운 위치가 계산되면 Residual과 Sensor Reliability를 다시 계산한다.

위 과정은 총 3회 반복 수행하였다.

이를 통해 위치 추정 결과와 Sensor Reliability가 함께 수렴하도록 설계하였다.

반복 횟수를 증가시키면서 성능 변화를 비교한 결과, 1회, 2회, 3회 반복에서 순차적인 성능 향상이 나타났다.

다만 반복 횟수를 늘릴수록 계산 시간이 증가하므로, 성능 향상과 실행 시간을 함께 고려하여 iteration = 3을 최종 설정으로 채택하였다.

최종 반복 결과를 사용자 위치 추정값으로 반환한다.

---

# 3. Agent AI 활용 내용

본 프로젝트에서는 ChatGPT를 보조 도구로 활용하였다.

AI는 다음과 같은 역할을 수행하였다.

1. RTT 기반 위치 추정 관련 강건 추정 기법 조사
2. Huber Loss, MAD, Reliability Weighting 등의 개념 정리
3. Python 구현 과정의 오류 수정 지원
4. 알고리즘 아이디어 제안

반면 다음 작업은 직접 수행하였다.

1. 데이터 구조 분석
2. RTT 특성 분석
3. Residual 통계 분석
4. BS별 센서 특성 분석
5. 하이퍼파라미터 탐색
6. 성능 검증
7. 최종 알고리즘 선정

특히 AI가 제안한 모든 방법을 그대로 사용하지 않았으며, 실제 데이터에서 반복 실험을 수행하여 성능이 향상되는 경우에만 채택하였다.

예를 들어 Environment-Aware Scaling은 참신한 아이디어였지만 Validation 성능 향상이 확인되지 않아 최종 알고리즘에서 제외하였다.

따라서 AI는 아이디어 탐색 및 구현 보조 역할을 수행하였으며, 최종 설계와 검증은 직접 수행하였다.

# 4. 실험 결과 및 고찰

## 4.1 단계별 성능 변화

제안한 알고리즘의 각 구성 요소가 실제로 성능 향상에 기여하는지 확인하기 위하여 단계별 실험을 수행하였다.

### Baseline Least Squares

| Method        |  Mean | Median |   P90 |
| ------------- | ----: | -----: | ----: |
| Least Squares | 23.21 |  21.73 | 33.59 |

기본 Least Squares는 RTT 이상치에 매우 취약하였다. 일부 BS의 큰 거리 오차가 전체 위치 추정 결과를 크게 왜곡하였으며, 실제 환경에서는 사용하기 어려운 수준의 성능을 보였다.

---

### Huber Robust LS

| Method          |  Mean | Median |   P90 |
| --------------- | ----: | -----: | ----: |
| Huber Robust LS | 16.14 |  15.09 | 28.18 |

Huber Loss만 적용해도 큰 성능 향상이 나타났다.

이는 RTT 데이터에 포함된 극단적인 이상치가 위치 추정 성능 저하의 주요 원인 중 하나였음을 의미한다.

---

### Trust Weighting

| Method      |  Mean | Median |   P90 |
| ----------- | ----: | -----: | ----: |
| Trust-Huber | 15.29 |  13.92 | 27.71 |

센서 신뢰도 개념을 도입함으로써 추가적인 성능 향상을 확인하였다.

단순히 강건 최적화를 수행하는 것보다 각 BS의 측정 신뢰도를 반영하는 것이 효과적이라는 것을 확인하였다.

---

### MAD + Trust

| Method      |  Mean | Median |   P90 |
| ----------- | ----: | -----: | ----: |
| MAD + Trust | 15.18 |  13.57 | 27.60 |

극단적인 이상치를 억제하면서도 정상 센서의 정보를 유지할 수 있었다.

MAD 기반 Hard Filtering은 일부 심각한 NLOS 측정값의 영향을 감소시키는 데 효과적이었다.

---

### Bias Compensation

| Method       |  Mean | Median |   P90 |
| ------------ | ----: | -----: | ----: |
| Bias + Trust | 14.30 |  12.80 | 26.70 |

Residual 분석을 통해 RTT 측정값이 실제 거리보다 크게 측정되는 경향이 존재함을 확인하였다.

이를 바탕으로 Residual Median 기반 Bias Compensation을 적용하였다.

Bias Compensation은 Mean Error를 15.18 m에서 14.30 m로 감소시켰다.

이는 RTT 측정값에 체계적인 거리 오차가 실제로 존재함을 의미하며, Residual 기반 Bias 보정이 위치 추정 성능 향상에 효과적이라는 것을 확인하였다.

따라서 Bias Compensation은 최종 알고리즘에 포함하였다.

---

### Iterative Refinement

| Method               |  Mean | Median |   P90 |
| -------------------- | ----: | -----: | ----: |
| Iterative Trust-Bias | 12.38 |  10.33 | 25.44 |

반복적인 위치-신뢰도 갱신이 효과적임을 확인하였다.

초기 위치 추정 결과를 기반으로 신뢰도를 계산하고, 계산된 신뢰도를 다시 위치 추정에 반영하는 구조가 성능 향상에 기여하였다.

이를 통해 Position-Reliability Co-Refinement 구조의 유효성을 확인할 수 있었다.

---

## 4.2 최종 알고리즘

하이퍼파라미터 탐색 결과 다음 설정이 가장 우수한 성능을 보였다.

* trust_scale = 4.0
* reject_scale = 3.0
* iteration = 3

최종 결과는 다음과 같다.

| Method                                     |  Mean | Median |   P90 |
| ------------------------------------------ | ----: | -----: | ----: |
| Adaptive Iterative Trust-Bias Localization | 11.80 |   9.51 | 25.28 |

초기 Least Squares 대비 Mean Error는 약 49% 감소하였다.

또한 Median Error 역시 크게 감소하여 전반적인 위치 추정 안정성이 향상되었음을 확인하였다.

추가적으로 Failure Rate(오차 5 m 초과 비율)를 함께 분석한 결과, 초기 Least Squares의 99.71%에서 최종 알고리즘의 72.71%로 감소하였다. 이는 평균 성능뿐 아니라 큰 위치 오류를 줄이는 데에도 제안한 알고리즘이 효과적임을 의미한다.


---

## 4.3 일반화 성능 검증

최종 알고리즘이 특정 사용자 데이터에 과적합되지 않았는지 확인하기 위하여 Train / Validation 분할 실험을 수행하였다.

| Dataset    |  Mean | Median |   P90 |
| ---------- | ----: | -----: | ----: |
| Train      | 11.60 |   9.54 | 25.05 |
| Validation | 12.31 |   9.46 | 25.80 |

Train과 Validation의 성능 차이가 매우 작게 나타났다.

특히 Median Error는 거의 동일한 수준을 유지하였으며, 이는 제안한 알고리즘이 특정 사용자에 의존하지 않고 다양한 사용자 환경에서도 안정적으로 동작함을 의미한다.

또한 Environment-Aware Scaling과 같은 추가적인 적응형 방법도 실험하였으나 Validation 성능 향상이 확인되지 않아 최종 알고리즘에서는 제외하였다.

이는 단순히 아이디어를 추가하는 것보다 실제 검증 결과를 기준으로 알고리즘을 선택하는 것이 중요함을 보여준다.

---

## 4.4 연구 과정에서 발견한 핵심 아이디어 및 차별성

본 프로젝트는 단순히 이상치를 제거하는 방향으로 접근하지 않았다.

오히려 현재 위치 추정 결과와 RTT 측정값의 일관성을 이용하여 각 BS의 신뢰도를 계산하고, 계산된 신뢰도를 다시 위치 추정에 반영하는 Position-Reliability Co-Refinement 구조를 설계하였다.

이는 위치 추정과 센서 평가를 분리하지 않고 하나의 반복 구조 안에서 함께 수행한다는 점에서 기존 접근 방식과 차별화된다.

첫째, 센서를 제거하지 않고 모든 BS에 연속적인 신뢰도(Continuous Reliability)를 부여하였다.

일반적인 이상치 제거 방식은 특정 센서를 완전히 제외하지만, 본 방법은 Residual 기반 신뢰도를 계산하여 모든 센서 정보를 활용하면서도 이상치의 영향을 감소시킨다.

둘째, Residual 통계를 이용하여 RTT 거리 자체의 Bias를 추정하고 보정하였다.

데이터 분석 과정에서 RTT 측정값이 실제 거리보다 크게 측정되는 경향을 확인하였으며, 이를 이용한 Adaptive Bias Compensation을 적용하였다.

셋째, 위치 추정과 센서 신뢰도 계산을 반복적으로 수행하는 Position-Reliability Co-Refinement 구조를 설계하였다.

현재 위치 추정 결과를 이용하여 센서 신뢰도를 계산하고, 계산된 신뢰도를 다시 위치 추정에 반영함으로써 위치와 신뢰도가 함께 수렴하도록 하였다.

본 프로젝트의 핵심 아이디어는 단순히 이상치를 제거하는 것이 아니라, 현재 위치 추정 결과와 측정값의 일관성을 이용하여 센서 신뢰도를 계산하고 이를 다시 위치 추정에 반영하는 것이다.

실험 결과 각 단계는 독립적으로도 성능 향상을 보였으며, 최종적으로 Mean Error를 23.21 m에서 11.80 m까지 감소시킬 수 있었다.

또한 Train/Validation 실험에서도 유사한 성능을 보여 특정 사용자에 과적합되지 않았음을 확인하였다.

이러한 결과를 통해 제안한 Adaptive Iterative Trust-Bias Localization 알고리즘이 다양한 NLOS 환경에서도 강건한 위치 추정을 수행할 수 있음을 확인하였다.

---

# 5. 참고문헌

[1] P. J. Huber, "Robust Estimation of a Location Parameter", Annals of Mathematical Statistics, 1964.

[2] Hampel, Ronchetti, Rousseeuw and Stahel, Robust Statistics: The Approach Based on Influence Functions, Wiley, 1986.

[3] SciPy Documentation, scipy.optimize.least_squares.

[4] 스마트모빌리티공학실험2 기말 프로젝트 가이드라인.
