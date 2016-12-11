from __future__ import division
from __future__ import print_function
from __future__ import with_statement

import sys
import quantities as pq
import os
import glob
import numpy as np
import exdir


def parse_params(text):
    params = {}

    for line in text.split("\n"):
        line = line.strip()

        if len(line) == 0:
            continue

        line_splitted = line.split(" ", 1)

        name = line_splitted[0]
        params[name] = None

        if len(line_splitted) > 1:
            try:
                params[name] = int(line_splitted[1])
            except:
                try:
                    params[name] = float(line_splitted[1])
                except:
                    params[name] = line_splitted[1]
    return params


def parse_header_and_leave_cursor(file_handle):
    header = ""
    while True:
        search_string = "data_start"
        byte = file_handle.read(1)
        header += str(byte, 'latin-1')

        if not byte:
            raise IOError("Hit end of file '" + eeg_filename + "'' before '" + search_string + "' found.")

        if header[-len(search_string):] == search_string:
            break

    params = parse_params(header)

    return params


def assert_end_of_data(file_handle):
    remaining_data = str(file_handle.read(), 'latin1')
    assert(remaining_data.strip() == "data_end")


def scale_analog_signal(value, gain, adc_fullscale_mv, bytes_per_sample):
    """
    Takes value as raw sample data and converts it to millivolts quantity.

    The mapping in the case of bytes_per_sample = 1 is

        [-128, 127] -> [-1.0, (127.0/128.0)] * adc_fullscale_mv / gain (mV)

    The correctness of this mapping has been verified by contacting Axona.
    """
    if type(value) is np.ndarray and value.base is not None:
        raise ValueError("Value passed to scale_analog_signal cannot be a numpy view because we need to convert the entire array to a quantity.")
    max_value = 2**(8 * bytes_per_sample - 1)  # 128 when bytes_per_sample = 1
    result = (value / max_value) * (adc_fullscale_mv / gain)
    result = result
    return result


class AxonaFile:
    """
    Class for "reading" experimental data from an Axona dataset.
    """
    def __init__(self, filename):
        self._absolute_filename = filename
        self._path, relative_filename = os.path.split(filename)
        self._base_filename, extension = os.path.splitext(relative_filename)

        if extension != ".set":
            raise ValueError("file extension must be '.set'")

        with open(self._absolute_filename, "r") as f:
            text = f.read()

        params = parse_params(text)

        self._adc_fullscale = float(params["ADC_fullscale_mv"]) * 1000.0 * pq.uV
        self._duration = float(params["duration"]) * pq.s  # TODO convert from samples to seconds
        self._tracked_spots_count = int(params["tracked_spots"])
        self._params = params

        # TODO this file reading can be removed, perhaps?
        channel_group_files = glob.glob(os.path.join(self._path, self._base_filename) + ".[0-9]*")

        self._channel_to_channel_index = {}
        self._channel_group_to_channel_index = {}
        self._channel_count = 0
        self._channel_group_count = 0
        self._channel_indexes = []
        for channel_group_file in channel_group_files:
            # increment before, because channel_groups start at 1
            self._channel_group_count += 1
            group_id = self._channel_group_count
            with open(channel_group_file, "rb") as f:
                channel_group_params = parse_header_and_leave_cursor(f)
                num_chans = channel_group_params["num_chans"]
                channel_ids = []
                channel_names = []
                for i in range(num_chans):
                    channel_id = self._channel_count + i
                    channel_ids.append(channel_id)
                    channel_names.append("channel_{}_group_{}_internal_{}".format(channel_id, group_id, i))

                channel_index = {"group_id": group_id,
                                 "channel_names": np.array(channel_names, dtype="S"),
                                 "channel_ids": np.array(channel_ids),
                                 "analogsignals": [],
                                 "spiketrains": []}
                self._channel_indexes.append(channel_index)
                self._channel_group_to_channel_index[group_id] = channel_index

                for i in range(num_chans):
                    channel_id = self._channel_count + i
                    self._channel_to_channel_index[channel_id] = channel_index

                # increment after, because channels start at 0
                self._channel_count += num_chans

        # TODO add channels only for files that exist
        self._channel_ids = np.arange(self._channel_count)

        # TODO read the set file and store necessary values as attributes on this object

    def _channel_gain(self, channel_group_index, channel_index):
        # TODO split into two functions, one for mapping and one for gain lookup
        global_channel_index = channel_group_index * 4 + channel_index
        param_name = "gain_ch_{}".format(global_channel_index)
        return float(self._params[param_name])

    def read_block(self,
                   lazy=False,
                   cascade=True):
        """
        Arguments:
            Channel_index: can be int, iterable or None to select one, many or all channel(s)

        """

        blk = Block()
        if cascade:
            seg = Segment(file_origin=self._absolute_filename)

            blk.channel_indexes = self._channel_indexes

            blk.segments += [seg]

            seg.analogsignals = self.read_analogsignal(lazy=lazy, cascade=cascade)
            seg.irregularlysampledsignals = self.read_tracking()
            seg.spiketrains = self.read_spiketrain()

            # TODO Call all other read functions

            seg.duration = self._duration

            # TODO May need to "populate_RecordingChannel"

            # spiketrain = self.read_spiketrain()

            # seg.spiketrains.append()

        blk.create_many_to_one_relationship()
        return blk

    def read_epoch():
        # TODO read epoch data
        pass

    def read_spiketrain(self):
        # TODO add parameter to allow user to read raw data or not?
        spike_trains = []

        channel_group_files = glob.glob(os.path.join(self._path, self._base_filename) + ".[0-9]*")
        for raw_filename in sorted(channel_group_files):
            with open(raw_filename, "rb") as f:
                params = parse_header_and_leave_cursor(f)

                channel_group_index = int(raw_filename.split(".")[-1])
                bytes_per_timestamp = params.get("bytes_per_timestamp", 4)
                bytes_per_sample = params.get("bytes_per_sample", 1)
                num_spikes = params.get("num_spikes", 0)
                num_chans = params.get("num_chans", 1)
                samples_per_spike = params.get("samples_per_spike", 50)
                timebase = int(params.get("timebase", "96000 hz").split(" ")[0]) * pq.Hz

                bytes_per_spike_without_timestamp = samples_per_spike * bytes_per_sample
                bytes_per_spike = bytes_per_spike_without_timestamp + bytes_per_timestamp

                timestamp_dtype = ">u" + str(bytes_per_timestamp)
                waveform_dtype = "<i" + str(bytes_per_sample)

                dtype = np.dtype([("times", (timestamp_dtype, 1), 1), ("waveforms", (waveform_dtype, 1), samples_per_spike)])

                data = np.fromfile(f, dtype=dtype, count=num_spikes * num_chans)
                assert_end_of_data(f)

            times = data["times"][::4] / timebase  # time for each waveform is the same, so we take each fourth time
            waveforms = data["waveforms"]
            # TODO ensure waveforms is properly reshaped
            waveforms = waveforms.reshape(num_spikes, num_chans, samples_per_spike)
            waveforms = waveforms.astype(float)

            channel_gain_matrix = np.ones(waveforms.shape)
            for i in range(num_chans):
                channel_gain_matrix[:, i, :] *= self._channel_gain(channel_group_index, i)

            waveforms = scale_analog_signal(waveforms,
                                            channel_gain_matrix,
                                            self._adc_fullscale,
                                            bytes_per_sample)

            # TODO get proper t_stop
            spike_train = {
                "times": times,
                "waveforms": waveforms,
                "num_spikes": num_spikes,
                "num_chans": num_chans,
                "samples_per_spike": samples_per_spike
            }
            # spike_trains.append(spike_train)
            channel_index = self._channel_group_to_channel_index[channel_group_index]
            # unit = Unit()
            # unit.spiketrains.append(spike_train)
            channel_index["spiketrains"].append(spike_train)

        return spike_trains

    def read_tracking(self):
        """
        Read tracking data_end
        """
        # TODO fix for multiple .pos files if necessary
        # TODO store attributes, such as pixels_per_metre
        pos_filename = os.path.join(self._path, self._base_filename+".pos")
        if not os.path.exists(pos_filename):
            raise IOError("'.pos' file not found:" + pos_filename)

        with open(pos_filename, "rb") as f:
            params = parse_header_and_leave_cursor(f)
            # print(params)

            sample_rate_split = params["sample_rate"].split(" ")
            assert(sample_rate_split[1] == "hz")
            sample_rate = float(sample_rate_split[0]) * pq.Hz  # sample_rate 50.0 hz

            eeg_samples_per_position = float(params["EEG_samples_per_position"])  # TODO remove?
            pos_samples_count = int(params["num_pos_samples"])
            bytes_per_timestamp = int(params["bytes_per_timestamp"])
            bytes_per_coord = int(params["bytes_per_coord"])

            timestamp_dtype = ">i" + str(bytes_per_timestamp)
            coord_dtype = ">i" + str(bytes_per_coord)

            bytes_per_pixel_count = 4
            pixel_count_dtype = ">i" + str(bytes_per_pixel_count)

            bytes_per_pos = (bytes_per_timestamp + 2 * self._tracked_spots_count * bytes_per_coord + 8)  # pos_format is as follows for this file t,x1,y1,x2,y2,numpix1,numpix2.

            # read data:
            dtype = np.dtype([("t", (timestamp_dtype, 1)),
                              ("coords", (coord_dtype, 1), 2 * self._tracked_spots_count),
                              ("pixel_count", (pixel_count_dtype, 1), 2)])

            data = np.fromfile(f, dtype=dtype, count=pos_samples_count)
            assert_end_of_data(f)


            time_scale = float(params["timebase"].split(" ")[0]) * pq.Hz
            times = data["t"].astype(float) / time_scale

            length_scale = float(params["pixels_per_metre"]) / pq.m
            coords = data["coords"].astype(float) / length_scale
            # positions with value 1023 are missing
            for i in range(2 * self._tracked_spots_count):
                coords[np.where(data["coords"][:, i] == 1023)] = np.nan * pq.m

            return times, coords


    def read_analogsignal(self,
                          lazy=False,
                          cascade=True):
        """
        Read raw traces
        Arguments:
            channel_index: must be integer array
        """

        # TODO read for specific channel

        # TODO check that .egf file exists

        analog_signals = []
        eeg_basename = os.path.join(self._path, self._base_filename)
        eeg_files = glob.glob(eeg_basename + ".eeg")
        eeg_files += glob.glob(eeg_basename + ".eeg[0-9]*")
        eeg_files += glob.glob(eeg_basename + ".egf")
        eeg_files += glob.glob(eeg_basename + ".egf[0-9]*")
        for eeg_filename in sorted(eeg_files):
            extension = os.path.splitext(eeg_filename)[-1][1:]
            file_type = extension[:3]
            suffix = extension[3:]
            if suffix == "":
                suffix = "1"
            suffix = int(suffix)
            with open(eeg_filename, "rb") as f:
                params = parse_header_and_leave_cursor(f)
                params["raw_filename"] = eeg_filename

                if file_type == "eeg":
                    sample_count = int(params["num_EEG_samples"])
                elif file_type == "egf":
                    sample_count = int(params["num_EGF_samples"])
                else:
                    raise IOError("Unknown file type. Should be .eeg or .efg.")

                sample_rate_split = params["sample_rate"].split(" ")
                bytes_per_sample = params["bytes_per_sample"]
                assert(sample_rate_split[1].lower() == "hz")
                sample_rate = float(sample_rate_split[0]) * pq.Hz  # sample_rate 250.0 hz

                if lazy:
                    # TODO Implement lazy loading
                    pass
                    # analog_signal = AnalogSignal([],
                    #                              units="uV",  # TODO get correct unit
                    #                              sampling_rate=sample_rate)
                    # we add the attribute lazy_shape with the size if loaded
                    # anasig.lazy_shape = self._attrs['shape'][0] # TODO do we need this
                else:
                    sample_dtype = (('<i' + str(bytes_per_sample), 1), params["num_chans"])
                    data = np.fromfile(f, dtype=sample_dtype, count=sample_count)
                    assert_end_of_data(f)

                    eeg_final_channel_id = self._params["EEG_ch_" + str(suffix)]
                    eeg_mode = self._params["mode_ch_" + str(eeg_final_channel_id)]
                    ref_id = self._params["b_in_ch_" + str(eeg_final_channel_id)]
                    eeg_original_channel_id = self._params["ref_" + str(ref_id)]

                    params["channel_id"] = eeg_original_channel_id

                    gain = self._params["gain_ch_{}".format(eeg_final_channel_id)]

                    signal = scale_analog_signal(data,
                                                 gain,
                                                 self._adc_fullscale,
                                                 bytes_per_sample)

                    # TODO read start time
                    # analog_signal = AnalogSignal(signal,
                                                #  units="uV",  # TODO get correct unit
                                                #  sampling_rate=sample_rate,
                                                #  **params)

                    analog_signal = {"signal": signal, "sample_rate": sample_rate, "units": "uV"}

                    # TODO what if read_analogsignal is called twice? The channel_index list should be cleared at some point
                    channel_index = self._channel_to_channel_index[eeg_original_channel_id]
                    channel_index["analogsignals"].append(analog_signal)

                analog_signals.append(analog_signal)

        return analog_signals


def set_general_attrs():
    params = {}
    params["session_id"] = ""
    params["institution"] = ""
    params["experimenter"] = ""
    params["lab"] = ""
    params["related_publications"] = ""
    params["notes"] = ""
    params["experiment_description"] = ""
    params["data_collection"] = ""
    params["stimulus"] = ""
    params["pharmacology"] = ""
    params["surgery"] = ""
    params["virus"] = ""
    params["slices"] = ""
    params["protocol"] = ""

    return params


def set_subject_attrs():
    params = {}
    params["subject_id"] = ""
    params["description"] = ""
    params["species"] = ""
    params["genotype"] = ""
    params["sex"] = ""
    params["age"] = ""
    params["weight"] = ""

    return params

if __name__ == "__main__":
    import getpass
    username = getpass.getuser()
    if username == "milad":
        path = "/home/milad/Dropbox/cinpla-shared/project/axonaio/2016-03-02-083928-1596/raw/02031602.set"
    elif username == "svenni":
        path = "/home/svenni/Dropbox/studies/cinpla/cinpla-shared/project/axonaio/2016-03-02-083928-1596/raw/02031602.set"
    axona_folder = AxonaFile(path)
    axona_folder.read_spiketrain()
    axona_folder.read_analogsignal()
    exdir_output = exdir.File("/tmp/test.exdir", "w")

    # TODO add general parameters
    general = exdir_output.create_group("general")
    general.attrs = set_general_attrs()
    subject = general.create_group("subject")
    subject.attrs = set_subject_attrs()

    processing = exdir_output.create_group("processing")

    # TODO for each shank, create LFP

    for channel_index in axona_folder._channel_indexes:
        shank = processing.create_group("shank_{}".format(channel_index["group_id"]))
        if len(channel_index["analogsignals"]) > 0:
            lfp = shank.create_group("LFP")

            for index, analog_signal in enumerate(channel_index["analogsignals"]):
                lfp_timeseries = lfp.require_group("LFP_timeseries_{}".format(index))
                lfp_timeseries.attrs["num_samples"] = 1  # TODO
                lfp_timeseries.attrs["starting_time"] = {
                    "value": 0.0,  # TODO
                    "unit": "s"
                }
                lfp_timeseries.attrs["sample_rate"] = analog_signal["sample_rate"]
                lfp_timeseries.attrs["electrode_idx"] = channel_index["channel_ids"]
                data = lfp_timeseries.create_dataset("data", data=analog_signal["signal"])

        if len(channel_index["spiketrains"]) > 0:
            event_waveform = shank.create_group("EventWaveform")

            for index, spiketrain in enumerate(channel_index["spiketrains"]):
                waveform_timeseries = event_waveform.create_group("waveform_timeseries_{}".format(index))
                waveform_timeseries.attrs["num_samples"] = spiketrain["num_spikes"]
                waveform_timeseries.attrs["sample_length"] = spiketrain["samples_per_spike"]
                waveform_timeseries.attrs["electrode_idx"] = channel_index["channel_ids"]
                waveform_timeseries.create_dataset("waveforms", data=spiketrain["waveforms"])
                waveform_timeseries.create_dataset("timestamps", data=spiketrain["times"])


    # TODO for each shank, create Event*

    # TODO create tracking
    tracking = processing.create_group("tracking")
    position = tracking.create_group("Position")

    times, coords = axona_folder.read_tracking()
    timestamps = position.create_dataset("timestamps", times)
    tracked_spots = int(coords.shape[1]/2)  # 2 coordinates per spot
    for n in range(tracked_spots):
        position.create_dataset("led_"+str(n), coords[:, n*2:n*2+1+1])
