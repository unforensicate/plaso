# -*- coding: utf-8 -*-
"""The processing status classes."""

import time

from plaso.lib import definitions


class CollectorStatus(object):
  """The collector status."""

  def __init__(self):
    """Initializes the collector status object."""
    super(CollectorStatus, self).__init__()
    self.identifier = None
    self.last_running_time = 0
    self.number_of_path_specs = 0
    self.pid = None
    self.status = None


class ExtractionWorkerStatus(object):
  """The extraction worker status."""

  def __init__(self):
    """Initializes the extraction worker status object."""
    super(ExtractionWorkerStatus, self).__init__()
    self.display_name = None
    self.identifier = None
    self.last_running_time = 0
    self.number_of_events = 0
    self.number_of_events_delta = 0
    self.number_of_path_specs = 0
    self.pid = None
    self.process_status = None
    self.status = None


class ProcessingStatus(object):
  """The processing status."""

  # The idle timeout in seconds.
  _IDLE_TIMEOUT = 5 * 60

  def __init__(self):
    """Initializes the processing status object."""
    super(ProcessingStatus, self).__init__()
    self._collector = None
    self._collector_completed = False
    self._extraction_workers = {}
    self._last_running_time = 0
    self._number_of_events = 0

  @property
  def extraction_workers(self):
    """The extraction worker status objects sorted by identifier."""
    return [
        self._extraction_workers[identifier]
        for identifier in sorted(self._extraction_workers.keys())]

  def GetExtractionCompleted(self):
    """Determines the extraction completed status.

    Returns:
      A boolean value indicating the extraction completed status.
    """
    number_of_path_specs = self.GetNumberOfExtractedPathSpecs()

    # TODO: include the path specs generated by the workers.
    if (self._collector_completed and
        self._collector.number_of_path_specs == number_of_path_specs):
      # TODO: this is not fully reliable, introduce waiting 3 times or equiv.
      return not self.WorkersRunning()

    return False

  def GetNumberOfExtractedEvents(self):
    """Retrieves the number of extracted events."""
    number_of_events = 0
    for extraction_worker_status in self._extraction_workers.itervalues():
      number_of_events += extraction_worker_status.number_of_events
    return number_of_events

  def GetNumberOfExtractedPathSpecs(self):
    """Retrieves the number of extracted path specifications."""
    number_of_path_specs = 0
    for extraction_worker_status in self._extraction_workers.itervalues():
      number_of_path_specs += extraction_worker_status.number_of_path_specs
    return number_of_path_specs

  def GetProcessingCompleted(self):
    """Determines the processing completed status.

    Returns:
      A boolean value indicating the extraction completed status.
    """
    extraction_completed = self.GetExtractionCompleted()
    number_of_events = self.GetNumberOfExtractedEvents()
    if (extraction_completed and
        self._number_of_events == number_of_events):
      return True

    return False

  def UpdateCollectorStatus(
      self, identifier, pid, number_of_path_specs, status):
    """Updates the collector status.

    Args:
      identifier: the extraction worker identifier.
      pid: the extraction worker process identifier (PID).
      number_of_path_specs: the total number of path specifications
                            processed by the extraction worker.
      status: the collector status.
    """
    if not self._collector:
      self._collector = CollectorStatus()

    self._collector.identifier = identifier
    self._collector.number_of_path_specs = number_of_path_specs
    self._collector.pid = pid
    self._collector.status = status

    if status == definitions.PROCESSING_STATUS_COMPLETED:
      self._collector_completed = True
    else:
      self._collector.last_running_time = time.time()

  def UpdateExtractionWorkerStatus(
      self, identifier, pid, display_name, number_of_events,
      number_of_path_specs, status, process_status):
    """Updates the extraction worker status.

    Args:
      identifier: the extraction worker identifier.
      pid: the extraction worker process identifier (PID).
      display_name: the display name of the file entry currently being
                    processed by the extraction worker.
      number_of_events: the total number of events extracted
                        by the extraction worker.
      number_of_path_specs: the total number of path specifications
                            processed by the extraction worker.
      status: the extraction worker status.
      process_status: the process status.
    """
    if identifier not in self._extraction_workers:
      self._extraction_workers[identifier] = ExtractionWorkerStatus()

    extraction_worker_status = self._extraction_workers[identifier]

    number_of_events_delta = (
        number_of_events - extraction_worker_status.number_of_events)

    extraction_worker_status.display_name = display_name
    extraction_worker_status.identifier = identifier
    extraction_worker_status.number_of_events = number_of_events
    extraction_worker_status.number_of_events_delta = number_of_events_delta
    extraction_worker_status.number_of_path_specs = number_of_path_specs
    extraction_worker_status.pid = pid
    extraction_worker_status.process_status = process_status
    extraction_worker_status.status = status

    if number_of_events_delta > 0:
      timestamp = time.time()
      extraction_worker_status.last_running_time = timestamp
      self._last_running_time = timestamp

  def UpdateStorageWriterStatus(self, number_of_events):
    """Updates the storage writer status.

    Args:
      number_of_events: the total number of events received
                        by the storage writer.
    """
    self._number_of_events = number_of_events

  def WorkersIdle(self):
    """Determines if the workers are idle."""
    timestamp = time.time()
    if (self._last_running_time > 0 and
        self._last_running_time < timestamp and
        timestamp - self._last_running_time >= self._IDLE_TIMEOUT):
      return True
    else:
      return False

  def WorkersRunning(self):
    """Determines if the workers are running."""
    for extraction_worker_status in self._extraction_workers.itervalues():
      if extraction_worker_status.number_of_events_delta > 0:
        return True
    return False
