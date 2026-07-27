# Week 11 Computer Vision Assignment

This workspace is set up to keep the model training and AI work in the notebook, the presentation layer in HTML/CSS/JS, and the process documentation in Markdown.

## Screen Recording
https://github.com/user-attachments/assets/ac79f09b-0563-4d35-9bd7-4ae03332c722
## Files

- `W11_CV_Assignment_Notebook.ipynb`: main assignment notebook with Q1-Q20 implementations
- `environment.yml`: CUDA-ready Conda environment definition
- `docs/setup.md`: environment and GPU setup notes
- `docs/process.md`: implementation log and workflow notes
- `web/index.html`: lightweight results dashboard
- `web/styles.css`: dashboard styling
- `web/app.js`: dashboard interactivity
- `tools/update_notebook.py`: helper script that patches the assignment notebook scaffold

## Intended workflow

1. Create the Conda environment from `environment.yml`.
2. Open the notebook with GPU enabled.
3. Run all cells top to bottom.
4. Review generated metrics and exported ONNX model.
5. Open the static dashboard in `web/` to present the outcomes.
