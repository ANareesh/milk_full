import React from "react";
import MilkCollectionForm from "../../components/MilkCollectionForm";
import { useAuth } from "../../context/AuthContext";

const CollectMilkPage = () => {
  const { user, token } = useAuth();
  // Assume agent selects a farmer from a list, or pass farmerId as prop
  const farmerId = /* get selected farmer id */;

  return (
    <div>
      <MilkCollectionForm
        farmerId={farmerId}
        token={token}
        onSuccess={() => alert("Milk collection recorded!")}
      />
    </div>
  );
};

export default CollectMilkPage;