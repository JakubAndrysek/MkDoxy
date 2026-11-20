/** A small API used by MkDoxy's integration tests. */
class DirectionExample {
public:
    /**
     * Transform a value.
     * @param[in] source Input value to read.
     * @param[out] destination Output value to write.
     * @param[in,out] state State value to update.
     * @param plain Value without a direction annotation.
     */
    void transform(int source, int &destination, int &state, int plain);
};
