from src.settings import *
from utils.imgnet_classifier.imgnet_settings import *
from utils.imgnet_classifier.imgnet_utils import ImgNetUtils
emb = ImgNetUtils()


def load_feature_and_label():
    sys.stdout.write(' load feature and labels \n')

    feature_data_path = FEATURES
    feature_label_path = LABELS

    if not os.path.exists(feature_data_path):
        sys.stderr.write(" not exist train data {}\n".format(feature_data_path))
        sys.exit(0)
    if not os.path.exists(feature_label_path):
        sys.stderr.write(" not exist train label {}\n".format(feature_label_path))
        sys.exit(0)

    data = []
    labels = []
    label_names = []
    # --- loading labels ---------------------------------------------------------------------
    sys.stdout.write(' loading training labels ... \n')
    with open(feature_label_path, 'r') as fp:
        for line in fp:
            line = line.replace('\n', '')
            label_names.append(line)

    # --- loading data -----------------------------------------------------------------------
    sys.stdout.write(' loading training data ... \n')
    with open(feature_data_path) as fp:  # for python 2x
        csv_reader = csv.reader(fp, delimiter=',')
        for row in csv_reader:
            _feature = [float(row[i]) for i in range(0, len(row))]
            _label = _feature[-2:]
            data.append(np.asarray(_feature[:-len(label_names)]))

            label_idx = -1
            for i in range(len(label_names)):
                if _label[i] == 1.0:
                    label_idx = i
                    break
            if label_idx != -1:
                labels.append(label_names[label_idx])
            else:
                sys.stderr.write(' error on tails for label indicator\n')
                sys.exit(0)
    return data, labels, label_names


def train():
    sys.stdout.write('>>> train \n')
    classifier_path = CLASSIFIER

    # --- load feature and label data ----------------------------------------------------------------
    data, labels, label_names = load_feature_and_label()

    # --- training -----------------------------------------------------------------------------------
    sys.stdout.write(' training... \n')
    classifier = SVC(C=1.0, kernel='linear', degree=3, gamma='auto', coef0=0.0, shrinking=True, probability=True,
                     tol=0.001, cache_size=200, class_weight='balanced', verbose=False, max_iter=-1,
                     decision_function_shape='ovr', random_state=None)

    classifier.fit(data, labels)
    joblib.dump(classifier, classifier_path)

    sys.stdout.write('>>> finished the training!\n')


def load_classifier_model():
    classifier_path = CLASSIFIER

    if not os.path.exists(classifier_path):
        sys.stderr.write(" not exist trained classifier {}\n".format(classifier_path))
        sys.exit(0)

    try:
        # loading
        model = joblib.load(classifier_path)
        return model
    except Exception as ex:
        print(ex)
        sys.exit(0)


def check_precision():
    # --- load trained classifier imgnet --------------------------------------------------------------
    classifier = load_classifier_model()

    sys.stdout.write('\n>>> checking the precision... \n')

    # --- load feature and label data ----------------------------------------------------------------
    data, labels, label_names = load_feature_and_label()

    true_pos = 0
    false_pos = 0
    true_neg = 0
    false_neg = 0
    # --- check confuse matrix ------------------------------------------------------------------------
    for i in range(len(data)):
        feature = data[i]
        feature = feature.reshape(1, -1)

        # Get a prediction from the imgnet including probability:
        probab = classifier.predict_proba(feature)

        max_ind = np.argmax(probab)
        sort_probab = np.sort(probab, axis=None)[::-1]  # Rearrange by size

        if sort_probab[0] / sort_probab[1] < 0.7:
            predlbl = "UnKnown"
        else:
            predlbl = classifier.classes_[max_ind]

        if labels[i] == "positive":
            if predlbl == labels[i]:
                true_pos += 1
            else:
                false_pos += 1
        else:
            if predlbl == labels[i]:
                true_neg += 1
            else:
                false_neg += 1

    sys.stdout.write('>>> precision result\n')
    sys.stdout.write("\tpositive : (true) {},  (false){}\n".format(true_pos, false_pos))
    sys.stdout.write("\tnegative : (false){},  (true) {}\n".format(false_neg, true_neg))
    total = len(data)
    precision = (true_neg + true_pos) / total
    sys.stdout.write("\tprecision : {} / {} : {}%\n".format(true_neg + true_pos, total, round(precision * 100, 2)))


if __name__ == '__main__':
    train()
    check_precision()
