from pipelines.training_pipeline import training_pipeline
import datetime
from datetime import timedelta
from zenml.pipelines import Schedule

def main(path: str='data', batch_size: int=32, epochs: int=20, hp_tuning_epochs: int=1, timedelta: int=30):
    """Run the training  pipeline."""


    training_pipeline(path=path, batch_size=batch_size, epochs=epochs, hp_tuning_epochs=hp_tuning_epochs, timedelta=timedelta)


    '''
    #
    # run the pipeline on a schedule once every day for 5 days (remove comment formatting in code for scheduled execution)
    #

    schedule = Schedule(
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(days=5),
        interval_second=86.400,
    )

    training_pipeline(path=path, batch_size=batch_size, epochs=epochs, hp_tuning_epochs=hp_tuning_epochs).run(schedule=schedule)
    '''

if __name__ == "__main__":
    main()
