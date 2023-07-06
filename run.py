from pipelines.training_pipeline import training_pipeline

def main(path: str='data', batch_size: int=32, epochs: int=5):
    """Run the training  pipeline."""

    training_pipeline(path=path, batch_size=batch_size, epochs=epochs)


if __name__ == "__main__":
    main()