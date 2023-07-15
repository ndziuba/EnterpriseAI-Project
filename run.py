from pipelines.training_pipeline import training_pipeline
import datetime
from datetime import timedelta
from zenml.pipelines import Schedule

def main(path: str='data', batch_size: int=32, epochs: int=5, hp_tuning_epochs: int=1):
    """Run the training  pipeline."""


    training_pipeline(path=path, batch_size=batch_size, epochs=epochs, hp_tuning_epochs=hp_tuning_epochs)


    '''
    #
    # run the pipeline on a schedule once every day for 5 weeks (remove comment formatting in code for scheduled execution)
    #

    schedule = Schedule(
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(weeks=5),
        interval_second=86.400,
    )

    training_pipeline(path=path, batch_size=batch_size, epochs=epochs, hp_tuning_epochs=hp_tuning_epochs).run(schedule=schedule)
    '''

if __name__ == "__main__":
    main()
