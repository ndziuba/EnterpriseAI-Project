from pipelines.training_pipeline import training_pipeline

def main(path: str='data', batch_size: int=32, epochs: int=1, hp_tuning_epochs: int=1):
    """Run the training  pipeline."""

    training_pipeline(path=path, batch_size=batch_size, epochs=epochs, hp_tuning_epochs=hp_tuning_epochs)

if __name__ == "__main__":
    main()
