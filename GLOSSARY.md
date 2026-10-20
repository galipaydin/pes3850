# PES 3850 — Plain-language glossary

Every technical term used in this course, explained without assuming a background in computing or mathematics. The week it first appears is given in brackets.

Keep this open during the labs. If a word in a notebook is not here, tell the instructor — it should be.

---

## The four big words

**Artificial intelligence (AI)** *(Week 1)* — a computer doing something we normally think requires human judgement. It is a **goal, not a method**. Saying a product "uses AI" tells you roughly as much as saying an athlete "does training".

**Machine learning** *(Week 1)* — learning the pattern from examples instead of being given a rule. Instead of writing "if the acute:chronic ratio exceeds 1.5, flag", you show the computer thousands of past cases and it finds the pattern.

**Deep learning** *(Week 1)* — machine learning that works from the raw thing itself: the pixels of a video, the waveform from a sensor. It builds up its own description in layers — edges, then shapes, then limbs, then a body. Nobody tells it what a knee looks like.

**Generative AI** *(Week 1)* — a model that produces something new — a paragraph, an image, a training plan, a piece of code — rather than a classification or a number.

**Large language model (LLM)** *(Week 1)* — a generative model trained on an enormous amount of text. ChatGPT, Claude and Gemini are large language models with a chat window on the front.

Each of these sits inside the one above it: every LLM is deep learning, all deep learning is machine learning, and all of it counts as AI.

---

## Models and how they learn

**Model** *(Week 1)* — the thing that came out of the learning. Give it an input, it gives you an output.

**Training data** *(Week 1)* — the past examples the model learned from. Almost every important question about a model is really a question about this.

**Feature** *(Week 4)* — an input variable. Age, jump height, weekly load. Also called an input or a predictor.

**Label** *(Week 4)* — the answer you already know for past cases, and want to predict for new ones. Also called the target or outcome.

**Training set / test set** *(Week 4)* — the athletes the model learned from, and the athletes held back to test it on. Testing on the training set measures memory, not skill.

**Cross-validation** *(Week 4)* — repeating the train/test split several times with different athletes held back each time, and averaging. A steadier estimate from the same data.

**Grouped cross-validation** *(Week 5)* — splitting so that an athlete is never in both the training and the test set. Essential whenever you have repeated measurements on the same people, which in sport is almost always.

**Supervised learning** *(Week 4)* — learning from examples where you know the answer.

**Unsupervised learning** *(Week 7)* — finding structure when there is no answer column. Most applied sport data is like this.

**Regression / classification** *(Week 4)* — predicting a number / predicting a category.

**Overfitting** *(Week 5)* — the model learned the noise and the individuals rather than the pattern. It looks excellent on the data it saw and fails on new athletes.

**Underfitting** *(Week 5)* — the model is too simple and missed the real pattern.

---

## The model families

You will never implement any of these. You will run them and choose between them.

**Linear regression** *(Week 4)* — fits a straight-line relationship between inputs and output. You already know it. It is a machine learning model.

**Ridge regression** *(Week 4)* — the same, reined in so that no single input dominates.

**Decision tree** *(Week 4)* — a flowchart of yes/no questions, learned from the data. The only model you can fully picture.

**Random forest** *(Week 4)* — hundreds of different decision trees, all voting.

**Gradient boosting** *(Week 4)* — trees built in sequence, each one fixing the previous one's mistakes.

**k-means** *(Week 7)* — the commonest clustering method. You choose how many groups; it sorts athletes into them.

**Principal component analysis (PCA)** *(Week 7)* — finds the few directions along which athletes genuinely differ. Eighteen tests are usually measuring three or four qualities.

---

## Judging a model

**Baseline** *(Week 5)* — the trivial rule your model has to beat. "Nobody will be injured" scores 93% accuracy. Compute this **first**, always.

**Accuracy** *(Week 5)* — how often the model is right. **Almost useless when the outcome is rare**, for exactly the reason above.

**Sensitivity** *(Week 5)* — of those who got injured, how many did we flag?

**Specificity** *(Week 5)* — of those who were fine, how many did we correctly leave alone?

**Precision** *(Week 5)* — of those we flagged, how many really were at risk?

**ROC-AUC** *(Week 5)* — can the model rank athletes by risk at all? 0.5 is a coin flip, 1.0 is perfect. Honest injury models sit around 0.73–0.77.

**PR-AUC** *(Week 5)* — the same question, but honest when the outcome is rare. Its baseline is the injury rate, not 0.5.

**Calibration** *(Week 5)* — when the model says 20%, do 20% of those athletes actually get injured? A model can rank well and still be badly calibrated.

**Mean absolute error (MAE)** *(Week 4)* — how far off a typical prediction is, in the units of the thing you predicted. The number to quote to a coach.

**R²** *(Week 4)* — the share of the variation the model accounts for.

**Threshold** *(Week 6)* — the probability above which you act. **A policy decision, not a statistical one**, and somebody has to make it.

**Cost matrix** *(Week 6)* — how much a missed case costs relative to a false alarm. The threshold follows from it.

**False alarm** *(Week 6)* — a flag on somebody who was fine. Counted per athlete per season, it is the number that decides whether a system is adopted.

**Base rate** *(Week 6)* — how often the outcome happens at all.

**Permutation importance** *(Week 4)* — shuffle one column and see how much worse the model gets. If nothing changes, it was not using it.

**Explainability** *(Week 6)* — describing what the model used. **Never a causal claim about the athlete.**

---

## Things that go wrong

**Data leakage** *(Week 5)* — information got into the model that would not be available at the moment you actually use it. The model is not predicting the future; it is reading an answer that was written down afterwards. In a real club export it arrives disguised as `availability_status`, `medical_flag` or `RTP_stage`.

**Class imbalance** *(Week 5)* — the outcome you care about is rare, so accuracy becomes meaningless.

**Distribution shift** *(Week 6)* — the athletes you use the model on are not like the athletes it learned from.

**Cross-subject generalisation** *(Week 9)* — whether a model trained on some people works on others. Usually worse than you expect.

**Hallucination** *(Week 2)* — a language model producing something fluent, confident and wrong. Not a malfunction; normal operation.

**Identity swap** *(Week 11)* — a tracking system confusing two players. Silent, and it corrupts every per-player number afterwards.

**Projection error** *(Week 10)* — the distortion from measuring a three-dimensional movement on a two-dimensional image.

**Algorithmic bias** *(Week 13)* — systematic error affecting some groups, learned from the training data and the world that produced it.

---

## Data

**Tidy data** *(Week 3)* — one row per observation, one column per variable. Adding an athlete adds rows, not columns.

**Long / wide format** *(Week 3)* — the shape for analysing / the shape for reading. You convert between them.

**Sampling rate** *(Week 3)* — how many times per second a sensor records. It decides what you are permitted to see. A 10 Hz unit cannot see a foot strike.

**Missing at random / missing for a reason** *(Week 3)* — whether the gaps in your data are unrelated to what you are studying. Wellness missing on the day after a match is **not** random.

**RPE — rating of perceived exertion** *(Week 3)* — the athlete's own answer to *how hard was that session?*, given about thirty minutes afterwards on a 0–10 scale (Borg's CR-10: 0 rest, 5 hard, 10 maximal). It measures the session from the inside; two athletes can run the same distance and rate it 3 and 8.

**Session load (sRPE)** *(Week 3)* — RPE × the session's minutes. A 90-minute session rated 7 is 630 units. The most widely used training-load measure in team sport, because it needs one question and a stopwatch, not a sensor.

**Join (merge)** *(Week 3)* — putting two tables together by matching a column they share, such as athlete and date. The commonest operation in applied analysis and the one that goes wrong most quietly: it can drop rows, or invent them, without any warning.

**Key** *(Week 3)* — the column or columns a join matches on. If the key is typed differently in the two files — `A07` and `a7` — those rows match nothing.

**Unit of analysis** *(Week 3)* — what one row stands for: a session, an athlete-week, an athlete. Decide it before you aggregate anything. Thirty athletes measured 170 times each are still thirty athletes.

**One-hot encoding** *(Week 3)* — turning a text column such as position into 0/1 columns a model can read, one per category. Four positions become three columns; the fourth is implied by the other three being zero.

**Imputation** *(Week 3)* — filling a gap with an estimated value: the column mean, the last value carried forward. It is never neutral — it is a claim about what the missing value would have been.

**Outlier / error** *(Week 3)* — an outlier is a value far from the rest; an error is a value that is wrong. They are not the same thing, and a statistical rule cannot tell them apart. A 3-standard-deviation rule removes about 0.3% of any normal column whether or not anything is wrong with it.

**Typical error** *(Week 3)* — the wobble you get when nothing has actually changed.

**Smallest worthwhile change** *(Week 3)* — the smallest difference that would matter in practice.

**Standardisation** *(Week 7)* — putting variables on a common scale so that units do not decide the answer.

**Windowing** *(Week 9)* — cutting a continuous signal into short slices and describing each with a handful of numbers, so it becomes an ordinary table.

**Feature extraction** *(Week 9)* — the numbers you compute per slice: mean, spread, range, dominant frequency.

**Event data** *(Week 11)* — a labelled record of every action in a match, with position and time.

**Expected goals (xG)** *(Week 11)* — the historical scoring probability of a shot like this one. It describes the chance created, **not** the finishing.

---

## Video and sensors

**Pixel** *(Week 10)* — one brightness value in the grid that is an image.

**Convolution** *(Week 10)* — a small window slid across an image, looking for one simple pattern such as an edge.

**Keypoint** *(Week 10)* — an estimated landmark on the body. MediaPipe places 33 of them.

**Pose estimation** *(Week 10)* — finding those keypoints in every frame.

**Markerless** *(Week 10)* — no physical markers attached to the athlete.

**Sagittal plane** *(Week 10)* — the side-on plane. What a single side camera can see, and the only plane it can measure.

**Flight time** *(Week 10)* — time airborne. Converts to jump height by *h = g·t²/8*.

**Limits of agreement** *(Week 10)* — the range within which two measurement methods agree 95% of the time.

**Detection / tracking / re-identification** *(Week 11)* — finding players in one frame / keeping their identity across frames / recovering identity after they were hidden.

**Homography** *(Week 11)* — the transform from image coordinates to pitch coordinates. Without it, tracking output is decoration.

**Accelerometer / gyroscope / magnetometer** *(Week 9)* — measures acceleration / rotation / direction. All three are in your phone.

**Acute:chronic workload ratio (ACWR)** *(Week 9)* — this week's load divided by the recent average. A cautionary tale about a metric that became doctrine before it was validated.

---

## Language models

**Token** *(Week 2)* — the unit a language model works in; roughly a word.

**Context window** *(Week 2)* — how much text it can hold in mind at once. Beyond it, earlier material falls away.

**Temperature** *(Week 2)* — the dial from predictable to inventive.

**Prompt** *(Week 2)* — what you send it. Role, task, context, format, constraints.

**Schema** *(Week 2)* — the structure of your data: the column names and what they contain. **Give it your schema, not a description.**

**Grounding** *(Week 12)* — requiring the model to answer from material you supplied.

**Retrieval-augmented generation (RAG)** *(Week 12)* — chunk your documents, index them, retrieve the relevant passages, put them in the prompt, get an answer with citations.

**Chunk** *(Week 12)* — one passage of a document, sized for retrieval.

**Agent** *(Week 12)* — a language model that can use tools and take actions.

**Bias probe** *(Week 12)* — asking the same question about different people and seeing what changes.

---

## Ethics and law

**Personal data** *(Week 3)* — data about an identifiable person. An athlete's GPS trace qualifies.

**Special-category data** *(Week 13)* — health and biometric data, with stricter legal protection under KVKK and GDPR.

**Biometric data** *(Week 13)* — data about the body that can identify a person.

**Anonymisation / pseudonymisation** *(Week 13)* — making a person unidentifiable / replacing names with codes. **They are not the same**, and a squad of 22 is frequently re-identifiable.

**Substantive consent** *(Week 13)* — consent that could genuinely have been refused.

**Data sovereignty** *(Week 13)* — who holds rights over data generated by a person's body. Legally unsettled.

**Relative age effect** *(Week 13)* — over-representation of athletes born early in the selection year. A model trained on historical selections learns it as though it were talent.

**Accountability chain** *(Week 13)* — who answers for a decision, from developer through vendor and club to the coach.

**KVKK / GDPR / EU AI Act** *(Week 13)* — Turkey's data protection law / Europe's / the European risk-tiered AI regulation.

**İAEK** *(Week 8)* — METU's Human Subjects Ethics Committee. Approval is required **before** collecting data from people.

---

## Tools

**Google Colab** *(Week 1)* — notebooks that run in a browser tab. Free. Nothing to install.

**Notebook** *(Week 1)* — a document made of text cells and code cells that you run one at a time.

**pandas** *(Week 3)* — the tool that holds a table in Python. You will read and modify it, never write it from scratch.

**scikit-learn** *(Week 4)* — where all the models in this course come from.

**MediaPipe** *(Week 10)* — pose estimation that runs on an ordinary laptop.

**Kinovea** *(Week 10)* — free, validated video analysis. Your manual reference.

**Phyphox** *(Week 9)* — a free phone app that turns your phone into a sensor logger.

**statsbombpy** *(Week 11)* — downloads free professional football event data.

**NotebookLM** *(Week 12)* — a grounded assistant over documents you upload, with no code at all.

**AI Use Log** *(Week 1)* — the record you attach to every submission: tool, prompt, output, and what you changed or rejected.
