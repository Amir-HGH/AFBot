import json
import logging
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from Codes.DataBase.DatabaseClass import B_Database_app


# --------------------------------------------------
# Configuration
# --------------------------------------------------

logger = logging.getLogger(__name__)

MODEL_PATH = Path(
    r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Semantic_Search\Model\E_AllMiniLM_L6V2\Model"
)

INDEX_PATH = Path(
    r"D:\Files\Pythone\AFilm Bot\Codes\Tools\Recommendation\Semantic_Search\Index\New Index.index"
)

BACKUP_VECTORS_PATH = Path(
    r"D:\Files\Pythone\AFilm Bot\Building\overview_vectors_backup.json"
)

EXPECTED_MOVIES = 3080
BATCH_SIZE = 64
HNSW_M = 32


# --------------------------------------------------
# Main
# --------------------------------------------------

def rebuild_semantic_index():

    connection = None
    cursor = None

    try:

        # 1. Validate paths

        if not MODEL_PATH.is_dir():
            raise FileNotFoundError(
                f"Model path does not exist: {MODEL_PATH}"
            )

        if INDEX_PATH.exists():
            raise FileExistsError(
                f"New index already exists: {INDEX_PATH}"
            )

        if BACKUP_VECTORS_PATH.exists():
            raise FileExistsError(
                f"Backup already exists: {BACKUP_VECTORS_PATH}"
            )

        # 2. Read database

        logger.info("Reading movies from database...")

        data = B_Database_app.get_data(
            "movie",
            ["id", "overview", "overview_vector"]
        )

        if data is False:
            raise RuntimeError(
                "Could not retrieve movie data."
            )

        if len(data) != EXPECTED_MOVIES:
            raise RuntimeError(
                f"Expected {EXPECTED_MOVIES} movies, "
                f"received {len(data)}."
            )

        # 3. Validate movie IDs

        movie_ids = [row[0] for row in data]

        if len(set(movie_ids)) != EXPECTED_MOVIES:
            raise RuntimeError(
                "Duplicate movie IDs detected."
            )

        # 4. Backup old vectors

        logger.info("Backing up old vectors...")

        BACKUP_VECTORS_PATH.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        old_vectors = [
            {
                "id": row[0],
                "overview_vector": row[2]
            }
            for row in data
        ]

        with open(
            BACKUP_VECTORS_PATH,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                old_vectors,
                file,
                ensure_ascii=False
            )

        # 5. Load model

        logger.info("Loading SentenceTransformer model...")

        model = SentenceTransformer(
            str(MODEL_PATH)
        )

        # 6. Generate embeddings

        logger.info("Generating new embeddings...")

        all_vectors = []

        for start in range(0, len(data), BATCH_SIZE):

            batch = data[start:start + BATCH_SIZE]

            texts = [
                row[1] if row[1] else ""
                for row in batch
            ]

            vectors = model.encode(
                texts,
                batch_size=BATCH_SIZE,
                convert_to_numpy=True,
                normalize_embeddings=False,
                show_progress_bar=False
            )

            vectors = np.asarray(
                vectors,
                dtype=np.float32
            )

            if vectors.ndim != 2:
                raise RuntimeError(
                    "Invalid embedding dimensions."
                )

            if vectors.shape[0] != len(batch):
                raise RuntimeError(
                    "Embedding count mismatch."
                )

            if not np.isfinite(vectors).all():
                raise RuntimeError(
                    "Embeddings contain invalid values."
                )

            all_vectors.append(vectors)

            logger.info(
                "Processed %d / %d movies",
                min(start + BATCH_SIZE, len(data)),
                len(data)
            )

        # 7. Combine vectors

        vectors = np.vstack(all_vectors)

        dimension = vectors.shape[1]

        if dimension <= 0:
            raise RuntimeError(
                "Invalid embedding dimension."
            )

        # Normalize all vectors

        faiss.normalize_L2(vectors)

        # 8. Build FAISS index

        logger.info(
            "Building FAISS index with dimension %d...",
            dimension
        )

        index = faiss.IndexIDMap2(
            faiss.IndexHNSWFlat(
                dimension,
                HNSW_M,
                faiss.METRIC_INNER_PRODUCT
            )
        )

        ids = np.asarray(
            movie_ids,
            dtype=np.int64
        )

        index.add_with_ids(
            vectors,
            ids
        )

        # 9. Validate index

        if index.d != dimension:
            raise RuntimeError(
                "Index dimension mismatch."
            )

        if index.ntotal != EXPECTED_MOVIES:
            raise RuntimeError(
                "Index vector count mismatch."
            )

        scores, search_ids = index.search(
            vectors[:1],
            1
        )

        if search_ids[0][0] == -1:
            raise RuntimeError(
                "Index search test failed."
            )

        # 10. Save new index

        logger.info("Saving New Index...")

        faiss.write_index(
            index,
            str(INDEX_PATH)
        )

        # 11. Reload and validate saved index

        test_index = faiss.read_index(
            str(INDEX_PATH)
        )

        if test_index.d != dimension:
            raise RuntimeError(
                "Saved index dimension mismatch."
            )

        if test_index.ntotal != EXPECTED_MOVIES:
            raise RuntimeError(
                "Saved index count mismatch."
            )

        # 12. Prepare database update

        logger.info("Preparing database update...")

        database_connection = B_Database_app.get_connection()

        if database_connection is False:
            raise RuntimeError(
                "Could not acquire database connection."
            )

        connection, cursor = database_connection

        database_values = [
            (
                json.dumps(
                    vector.tolist(),
                    separators=(",", ":")
                ),
                movie_id
            )
            for vector, movie_id in zip(vectors, movie_ids)
        ]

        # 13. Update database

        logger.info("Updating database vectors...")

        cursor.executemany(
            """
            UPDATE movie
            SET overview_vector = %s
            WHERE id = %s
            """,
            database_values
        )

        if cursor.rowcount != EXPECTED_MOVIES:
            raise RuntimeError(
                f"Updated rows mismatch: {cursor.rowcount}"
            )

        # 14. Commit

        connection.commit()

        logger.info(
            "Database successfully updated."
        )

        logger.info(
            "Rebuilding completed successfully. "
            "Movies: %d | Dimension: %d",
            EXPECTED_MOVIES,
            dimension
        )

        print("\nNew Index created successfully!")
        print("Index path:", INDEX_PATH)
        print("Index dimension:", dimension)
        print("Total vectors:", test_index.ntotal)

    except Exception:

        logger.exception(
            "Rebuilding semantic index failed."
        )

        if connection is not None:

            try:
                connection.rollback()

                logger.info(
                    "Database transaction rolled back."
                )

            except Exception:

                logger.exception(
                    "Database rollback failed."
                )

        raise

    finally:

        if connection is not None:

            B_Database_app.give_connection(
                connection,
                cursor
            )


if __name__ == "__main__":

    rebuild_semantic_index()


