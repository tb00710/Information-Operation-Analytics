# Within-Country Tweet Network Analysis

This project extracts selected fields from tweet CSV exports, loads an existing master pickle if desired, and analyzes retweet/reply interactions within and outside a country-specific collection of user IDs.

## Project layout

- `main.py` — runs the analysis workflow.
- `config.py` — country label, paths, and source CSV column positions.
- `data_loader.py` — loads source CSVs or an existing master pickle.
- `network_analysis.py` — calculates retweet/reply statistics and splits target interactions into within/outside collection.
- `exports.py` — writes the network outputs.
- `data/` — put local input files here (ignored by Git).
- `output/` — generated output files (ignored by Git).

## Setup

From this directory, create and activate a virtual environment if you use one, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Configure the run

Edit `config.py`:

- Set `COUNTRY` to the country/project label used in output filenames.
- Set `INPUT_FOLDER` to the folder containing source CSV files.
- Or set `MASTER_PICKLE` to a path to an existing master pickle, and set it to `None` to build from CSVs.

The original notebook used these zero-based CSV positions:

- `userid`: 1
- `accountDate`: 9
- `tweetDate`: 13
- `tweetClient`: 14
- `replyid`: 16
- `retweetid`: 19
- `mentions`: 29
- `text`: 12

Verify these positions against the current source CSV schema before processing new data.

## Run

```powershell
python main.py
```

Generated files are saved under `output/`.

## Notes about behavior

- Rows with repeated header values or too few columns are skipped by the CSV loader.
- Duplicate rows are removed before network statistics are calculated.
- A target is classified as "within collection" if its ID appears in the loaded dataset's `userid` column; otherwise it is classified as "outside collection."
- Percentages safely return 0 when the denominator is zero.
- The refactor fixes a clear notebook bug where the full reply-network export selected the retweet subset.
- Some filenames and the trimmed edge export structure are standardized compared with the notebook. If downstream tools consume the old files, compare and update those dependencies before replacing the original workflow.
- This project has been structurally validated, but the analysis has not been run against your private source datasets.
