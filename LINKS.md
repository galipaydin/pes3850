# PES 3850 — Links

Interactive pages worth opening during or after the lectures. All of them run in a browser, free,
with nothing to install. Each one says which week it belongs to and **one thing to try** — open it
with that question in mind rather than clicking around.

Words you do not know are in the [glossary](GLOSSARY.md).

---

## Week 2 — How a language model works

### Inside a language model, step by step
**[LLM Visualization](https://bbycroft.net/llm)** — Brendan Bycroft

A 3D, animated walk through a small GPT-style model, from the words going in to the next word
coming out. Every block of the model is drawn, and a guided walkthrough explains what happens in
each.

**Try this:** follow the walkthrough from the start and watch one token travel through the model.
Notice how much of the model is just arithmetic repeated many times — and that nowhere in it is
there a step that checks whether the answer is true.

### What an embedding is
**[LLM Embeddings Explained](https://huggingface.co/spaces/hesamation/primer-llm-embedding?section=what_are_embeddings%3F)** — Hugging Face

A visual guide to how a language model turns words into lists of numbers (embeddings), with
interactive plots. Nothing to type; read and scroll.

**Try this:** read the section *What are embeddings?*, which the link opens at. You need only one
idea from it: words used in similar ways end up with similar numbers, and that is how a model
"knows" that *sprint* and *run* are related.

### Embeddings you can play with
**[Embedding Playground](https://www.adityabawankule.io/tools/embedding-playground)** — Aditya Bawankule

Type sentences and watch them arrange themselves on a map by meaning, with the similarity between
any two shown as a number. No sign-up.

**Try this:** type three sentences about training load and two about nutrition, written in
different words. Do they separate into two groups? Then write one sentence that sits halfway
between, and see where it lands.

---

## Week 2 and Week 7 — Seeing data with many dimensions

### Ten thousand words, in three dimensions
**[Embedding Projector](https://projector.tensorflow.org/)** — TensorFlow

Thousands of word embeddings, each one hundreds of numbers long, squeezed down to three dimensions
so you can rotate them. Click a word to see its nearest neighbours.

**Try this:** search for a sport word and look at the list of its nearest neighbours. Then switch
the method on the left between **PCA** and **t-SNE**. PCA is the same method as on the Week 3
slides and in Lab 7 — here it is doing to word embeddings what it does there to fitness tests:
finding the few directions that carry most of the information.

---

*Found a good one? Send it to the instructor and it can go on this page.*
