
#include <QObject>

class CuteChinchilla : public QObject
{
    Q_OBJECT

public:
    enum class Species {
        ChinchillaChinchilla,
        ChinchillaLanigera
    };

    CuteChinchilla() { m_weight = 0; }
    int weight() const { return m_weight; }

public slots:
    /// Please weigh your pet regularly and set the new weight here.
    void setWeight(int weight);

signals:
    /// emitted when the weight of the Chinchilla changed.
    void weightChanged(int newWeight);

private slots:
    void foo();

private:
    int m_weight;
};
