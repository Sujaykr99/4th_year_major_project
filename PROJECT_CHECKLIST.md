# Matrix Project - Remaining Work Checklist

## 1. BACKEND AUDIT & CLEANUP

### Files to DELETE (Obsolete/Redundant)
- [ ] `backend/app/ml/so_preprocess_hierarchical.py` - V1 hierarchical (replaced by V2)
- [ ] `backend/app/ml/hierarchical_predictor.py` - V1 predictor (replaced by V2)
- [ ] `backend/app/ml/saved_models_sector/` - V1 sector models (replaced by V2)
- [ ] `backend/app/ml/saved_models_roles/` - V1 role models (replaced by V2)
- [ ] `backend/app/ml/phase1_reproduce_baseline.py` - Experimental
- [ ] `backend/app/ml/phase4_5_signal_ablation.py` - Experimental
- [ ] `backend/app/ml/so_train.py` - Old 11-class training
- [ ] `backend/app/ml/so_validate.py` - Old validation
- [ ] `backend/app/ml/train.py` - Old training script
- [ ] `backend/app/ml/pipeline.py` - Old pipeline (replaced by service.py)
- [ ] `backend/app/ml/train_role_classifiers.py` - V1 role training
- [ ] `backend/app/ml/train_sector_classifier.py` - V1 sector training
- [ ] `backend/check_data.py` - Old check script
- [ ] `backend/test_db.py` - Old test
- [ ] `backend/ml/saved_models_career/` - Old 11-class career model
- [ ] `backend/ml/plots/` - Old plots
- [ ] `backend/ml/plots_sector/` - V1 sector plots
- [ ] `backend/ml/plots_sector_v2/` - Can keep for reference
- [ ] `backend/ml/validation_plots/` - Old validation plots
- [ ] Root level CSV files (move to `data/` folder):
  - [ ] `matrix_dataset_baseline.csv`
  - [ ] `matrix_dataset_hierarchical.csv`
  - [ ] `matrix_dataset_hierarchical_v2.csv`
  - [ ] `matrix_dataset_so_v1.csv`
  - [ ] `phase1_baseline_results.json`
  - [ ] `phase4_5_results.json`
  - [ ] `so_preprocess_metadata.json`
  - [ ] `so_preprocess_hierarchical_metadata.json`
  - [ ] `so_preprocess_hierarchical_v2_metadata.json`
  - [ ] `readiness_scorer_config.json`

### Files to KEEP (Production)
- [x] `backend/app/ml/so_preprocess_hierarchical_v2.py` - V2 preprocessing
- [x] `backend/app/ml/hierarchical_predictor_v2.py` - V2 predictor
- [x] `backend/app/ml/readiness_scorer.py` - Placement readiness scorer
- [x] `backend/app/ml/train_placement.py` - Placement model training
- [x] `backend/app/ml/service.py` - Main ML service (needs update for V2)
- [x] `backend/app/ml/__init__.py`
- [x] `backend/app/api/v1/endpoints/prediction.py` - Prediction endpoints
- [x] `backend/app/api/v1/endpoints/profile.py` - Profile endpoints
- [x] `backend/app/api/v1/endpoints/roadmap.py` - Roadmap endpoints
- [x] `backend/app/api/v1/endpoints/auth.py` - Auth endpoints
- [x] `backend/app/models/schemas.py` - Pydantic schemas
- [x] `backend/app/services/roadmap_generator.py` - Roadmap generator
- [x] `backend/app/core/config.py` - Config
- [x] `backend/app/core/database.py` - Database
- [x] `backend/app/core/security.py` - Security
- [x] `backend/app/main.py` - FastAPI app entry
- [x] `backend/ml/saved_models_sector_v2/` - V2 sector model
- [x] `backend/ml/saved_models_roles_v2/` - V2 role models
- [x] `backend/ml/saved_models/` - Placement model
- [x] `backend/ml/model_card/hierarchical_v2_model_card.json` - Model card

### Files to REORGANIZE (Move to proper folders)
- [ ] Create `backend/data/` folder, move all CSV/JSON data files there
- [ ] Create `backend/ml/training/` folder for training scripts
- [ ] Create `backend/ml/inference/` folder for prediction code
- [ ] Create `backend/ml/models/` folder for saved models (already exists)


## 2. PLACEMENT MODEL FINALIZATION

- [ ] Check if placement dataset exists (`backend/data/` or root)
- [ ] Run placement training pipeline (`train_placement.py`)
- [ ] Evaluate placement model performance
- [ ] Save placement model artifacts to `backend/ml/saved_models/`
- [ ] Update ML service to load both career (hierarchical) AND placement models
- [ ] Add placement prediction endpoint
- [ ] Test placement prediction API


## 3. HIERARCHICAL CAREER MODEL INTEGRATION

- [ ] Create new `HierarchicalCareerService` class in `service.py` (or new file)
- [ ] Load sector + role models from `saved_models_sector_v2/` and `saved_models_roles_v2/`
- [ ] Update prediction endpoints to use hierarchical predictor
- [ ] Keep backward compatibility with existing `PredictionInput` schema
- [ ] Add sector confidence threshold logic
- [ ] Return hierarchical response: `{sector, role, confidence, sector_confidence, role_confidence}`


## 4. FILE ORGANIZATION & CLEANUP

- [ ] Delete obsolete files (listed above)
- [ ] Move data files to `backend/data/`
- [ ] Move training scripts to `backend/ml/training/`
- [ ] Move inference code to `backend/ml/inference/`
- [ ] Update imports in all affected files
- [ ] Verify no broken imports

---

## 5. TESTING & VERIFICATION

- [ ] Run smoke test: `python -m pytest backend/tests/test_smoke.py`
- [ ] Test career prediction endpoint with sample input
- [ ] Test placement prediction endpoint
- [ ] Test roadmap generation endpoint
- [ ] Verify model loading on startup
- [ ] Check API docs at `/docs`

---

## 6. DOCUMENTATION

- [ ] Update README with model architecture
- [ ] Document API endpoints
- [ ] Document model card location
- [ ] Document reproduction commands

---

## PRIORITY ORDER

1. **HIGH** - Finalize placement model (train + integrate)
2. **HIGH** - Integrate hierarchical V2 career model into API
3. **HIGH** - Clean up obsolete files
4. **MEDIUM** - Reorganize file structure
5. **MEDIUM** - Test all endpoints
6. **LOW** - Documentation updates