
class CancellationCheckMixin:
    """
    Mixin that provides cancellation check logic for pipeline services
    Requires host class to define:
        - self.cancel_requested: bool
        - self.logger
    """
    cancel_requested: bool # for type checkers

    def _should_continue_processing(self, level: str) -> bool:
        """
        Check if processing should continue or has been cancelled

        Args:
            level: Description of processing level, like post, comment, topic

        Returns:
            True if processing should continue, False if cancelled
        """
        if self.cancel_requested:
            self.logger.info(
                event_type=f"{self.__class__.__name__} run",
                message=f"Cancellation requested, stopping at {level} level",
            )
            return False
        return True
